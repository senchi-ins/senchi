from contextlib import asynccontextmanager
import os
import secrets
import sys
import json
import asyncio
import logging
from typing import Any, Union
from datetime import datetime
import uuid
import io
import base64
import qrcode
import subprocess
import threading
import time

import uvicorn
import pandas as pd
from pydantic import BaseModel
from fastapi import (
    FastAPI, 
    HTTPException, 
    Header, 
    WebSocket, 
    WebSocketDisconnect, 
    Depends, 
    Request,
    Query
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models.tokens import TokenRequest, TokenResponse
from monitor.config import settings
from monitor.models import (
    Device,
    DeviceType,
    NotificationResponse,
    LeakSensorResponse,
    NOTIFICATION_TYPES,
    LocationSetupRequest,
    SetupResponse,
    DeviceRequest,
)
from monitor.zbm import Monitor
from monitor.utils import get_all_model_fields
from notifications.noti import NotificationRouter
from rdsdb.rdsdb import RedisDB
from maindb.pg import PostgresDB

logger = logging.getLogger(__name__)

app_state = {
    "devices": {},
    "websocket_connections": {}, # Changed to dict keyed by user_id
    "mqtt_client": None,
    "notification_config": None,
    "active_leaks": set(),
    "notification_queue": asyncio.Queue()
}

def init_db():
    """
    Initialize the database connection.

    Note: Currently uses pd.df and written to a csv file.
    """
    # 2 tables are needed:
    # 1. devices
    # 2. notifications / device events
    # Temp database
    database = {
        "devices": pd.DataFrame(columns=list(Device.model_fields.keys())),
        "notifications": pd.DataFrame(columns=get_all_model_fields(NOTIFICATION_TYPES)),
    }
    return database

db = init_db()
mqtt_monitor = Monitor(app_state, db)
redis_db = RedisDB()
pg_db = PostgresDB()

# Add Redis and Postgres database to app_state so Monitor can access it
app_state["redis_db"] = redis_db
app_state["pg_db"] = pg_db

@asynccontextmanager
async def lifespan(app: FastAPI):

    loop = asyncio.get_running_loop()
    mqtt_monitor.loop = loop
    mqtt_monitor.start()
    
    # Initialize Redis connection with better error handling
    redis_connected = False
    try:
        logger.info("Attempting to connect to Redis...")
        redis_db.connect()  # Remove await - this is a synchronous method
        redis_connected = True
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        logger.error("Server will start without Redis functionality")
        logger.error("Please check your REDIS_URL environment variable")
        # Continue without Redis - some endpoints will fail but server won't crash
    
    # Start background thread for topic subscription only if Redis is connected
    if redis_connected:
        threading.Thread(
            target=subscribe_to_new_topics_periodically,
            args=(mqtt_monitor, redis_db),
            daemon=True
        ).start()
        logger.info("Background topic subscription thread started")
    else:
        logger.warning("Skipping background topic subscription due to Redis connection failure")
    
    logger.info("Home API Server started with integrated MQTT monitoring")
    yield
    
    mqtt_monitor.stop()
    
    # Clean up Redis connection
    if redis_connected:
        try:
            redis_db.disconnect()  # Remove await - this is a synchronous method
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    logger.info("Home API Server stopped")

app = FastAPI(lifespan=lifespan)

notification_router = NotificationRouter(redis_db)  

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_headers=settings.ALLOWED_HEADERS,
    allow_methods=settings.ALLOWED_METHODS,
)

async def get_current_user(authorization: str = Header(None)):
    """FastAPI dependency to validate JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_info = await notification_router.validate_token(token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_info

@app.get("/")
async def root():
    return {
        "message": "Home Automation API with Integrated Notifications",
        "version": "1.0.0",
        "mqtt_connected": mqtt_monitor.connected,
        "active_leaks": len(app_state["active_leaks"]),
        "total_devices": len(app_state["devices"])
    }


# TODO: Add a specific user id for the devices
@app.post("/devices")
async def get_devices(
    device_request: DeviceRequest,
    # token: str = Query(...)
):
    """Get all devices for a specific user"""
    # TODO: Validate the token
    user_id = device_request.user_id
    property_name = device_request.property_name
    
    cache_key = f"devices:{user_id}:{property_name}"
    print(f"Cache key: {cache_key}")
    cached_devices = app_state.get("devices", {}).get(cache_key)
    
    if cached_devices and "timestamp" in cached_devices:
        cache_age = datetime.now().timestamp() - cached_devices["timestamp"]
        if cache_age < 300:  # 5 minutes
            print(f"Returning cached devices: {cached_devices['devices']}")
            return cached_devices["devices"]
    
    print(f"Fetching devices from database for user: {user_id}, property: {property_name}")
    
    try:
        devices = app_state.get("pg_db").get_user_devices(user_id, property_name)
        print(f"Database returned devices: {devices}")
        
        # Only cache if we got actual results
        if devices:
            app_state["devices"][cache_key] = {
                "devices": devices,
                "timestamp": datetime.now().timestamp()
            }
            print(f"Cached {len(devices)} devices")
        else:
            print("No devices found, not caching empty result")
        
        return devices
        
    except Exception as e:
        logger.error(f"Error fetching devices from database: {e}")
        print(f"Database error: {e}")
        # Return empty list on error
        return []


# TODO: Delete, now on central server
@app.post("/api/auth/setup", response_model=TokenResponse)
async def setup_device_auth(request: TokenRequest):
    """Generate JWT token during device setup"""
    return await notification_router.create_user_token(
        device_serial=request.device_serial,
        push_token=request.push_token,
        email=request.email,
        full_name=request.full_name
    )

@app.post("/api/auth/push-token")
async def update_push_token(
    push_token: str,
    current_user: dict = Depends(get_current_user)
):
    """Update user's push notification token"""
    await notification_router.update_push_token(current_user["jwt_token"], push_token)
    return {"message": "Push token updated successfully"}

# TODO: Delete, now on central server
@app.get("/api/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if token is valid"""
    # TODO: Update to use actual token
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "location_id": current_user["location_id"],
        "device_serial": current_user.get("device_serial", ""),
        "full_name": current_user.get("full_name", ""),
        "expires_at": current_user["exp"]
    }

class LoginRequest(BaseModel):
    email: str

# TODO: Delete, now on central server
@app.post("/api/auth/login")
async def login_with_email(request: LoginRequest):
    """Login with email to retrieve stored token"""
    try:
        email = request.email
        # Get token from Redis using email
        token = redis_db.get_key(f"email:{email}")
        
        if not token:
            raise HTTPException(status_code=404, detail="No account found for this email")
        
        # Convert bytes to string if needed
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        # Validate the token
        user_info = await notification_router.validate_token(token)
        
        if not user_info:
            # Token is invalid, remove the mapping
            redis_db.delete_key(f"email:{email}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "message": "Login successful",
            "token": token,
            "user_info": user_info
        }
        
    except Exception as e:
        logger.error(f"Login failed for email {email}: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

from pydantic import BaseModel

class RedisSetRequest(BaseModel):
    key: str
    value: str
    ttl: int = None

@app.post("/redis/set")
def set_redis_key(request: RedisSetRequest):
    # print(f"Setting key: {request.key} with value: {request.value[:50]}... and ttl: {request.ttl}")
    logger.info(f"Setting key: {request.key} with ttl: {request.ttl}")
    redis_db.set_key(request.key, request.value, request.ttl)
    return {"message": "Key set successfully"}

# TODO: Delete
@app.get("/redis/get")
def get_redis_key(key: str):
    value = redis_db.get_key(key)
    return {"key": key, "value": value}

@app.post("/zigbee/permit-join")
async def permit_join(
    duration: int = 60,
    current_user: dict = Depends(get_current_user)
):
    """Allow new devices to join for the authenticated user's location"""
    logger.info(f"Permit join requested for {duration} seconds by user {current_user.get('user_id')}. MQTT connected: {mqtt_monitor.connected}")
    logger.info(f"Full user token data: {current_user}")
    
    if not mqtt_monitor.connected:
        print(f"MQTT not connected. Broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        logger.error(f"MQTT not connected. Broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        raise HTTPException(
            status_code=503, 
            detail=f"MQTT not connected to {settings.MQTT_BROKER}:{settings.MQTT_PORT}"
        )
    
    # Get the device serial from the user's JWT token
    device_serial = current_user.get('device_serial')
    logger.info(f"Extracted device serial: {device_serial}")
    print(f"Extracted device serial: {device_serial}")
    
    if not device_serial:
        logger.error(f"No device serial found in user token: {current_user}")
        raise HTTPException(status_code=400, detail="No device serial associated with user")
    
    # Construct the topic using the device serial
    topic = f"zigbee2mqtt/senchi-{device_serial}/bridge/request/permit_join"
    payload = json.dumps({"time": duration})
    
    logger.info(f"Publishing to topic: {topic}")
    logger.info(f"Payload: {payload}")
    logger.info(f"MQTT client state: connected={mqtt_monitor.client.is_connected()}")
    
    try:
        result = mqtt_monitor.client.publish(topic, payload)
        logger.info(f"Publish result: rc={result.rc}, mid={result.mid}")
        
        if result.rc == 0:
            logger.info(f"Permit join message published to {topic} successfully")
            return {
                "message": f"Permit join enabled for {duration} seconds",
                "topic": topic,
                "device_serial": device_serial,
                "publish_rc": result.rc,
                "publish_mid": result.mid
            }
        else:
            logger.error(f"MQTT publish failed with rc={result.rc}")
            raise HTTPException(status_code=500, detail=f"MQTT publish failed with rc={result.rc}")
            
    except Exception as e:
        logger.error(f"Error publishing permit join message to {topic}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish permit join: {str(e)}")
    

def broadcast_device_update(user_id: str, device_data: dict):
    """Broadcast device updates to connected WebSocket clients for a specific user"""
    if user_id not in app_state.get("websocket_connections", {}):
        return
    
    message = {
        "type": "device_update",
        "device_id": device_data.get("ieee_address") or device_data.get("serial_number"),
        "data": {
            "friendly_name": device_data.get("friendly_name"),
            "device_type": device_data.get("device_type"),
            "last_seen": device_data.get("last_seen"),
            "status": device_data.get("status", "active"),
            "battery": device_data.get("battery"),
            "water_leak": device_data.get("water_leak"),
            "linkquality": device_data.get("linkquality")
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to all connected WebSocket clients for this user
    disconnected_clients = []
    for websocket in app_state["websocket_connections"][user_id]:
        try:
            asyncio.create_task(websocket.send_text(json.dumps(message)))
        except Exception as e:
            logger.error(f"Failed to send device update to WebSocket: {e}")
            disconnected_clients.append(websocket)
    
    # Clean up disconnected clients
    for websocket in disconnected_clients:
        try:
            app_state["websocket_connections"][user_id].remove(websocket)
        except ValueError:
            pass  # Already removed
    
    # Remove empty user connections
    if not app_state["websocket_connections"][user_id]:
        del app_state["websocket_connections"][user_id]


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: str, 
    # token: str = Query(...)
):
    # TODO: Validate the token
    logger.info(f"WebSocket connection attempt for user_id: {user_id}")
    
    # Validate JWT
    # user_info = await notification_router.validate_token(token)

    await websocket.accept()
    logger.info(f"WebSocket connection accepted for user: {user_id}")
    
    # Store connection by user_id
    if user_id not in app_state["websocket_connections"]:
        app_state["websocket_connections"][user_id] = []
    app_state["websocket_connections"][user_id].append(websocket)
    logger.info(f"WebSocket connection stored for user: {user_id}")

    try:
        # Send initial state: fetch user's devices from database
        # For now, use "main" as default property - this should be configurable
        try:
            user_devices = app_state.get("pg_db").get_user_devices(user_id, "main")
            logger.info(f"Fetched {len(user_devices) if user_devices else 0} devices for user: {user_id}")
        except Exception as db_error:
            logger.error(f"Database error fetching devices for user {user_id}: {db_error}")
            user_devices = []
        
        # Send initial device state
        if user_devices:
            for device in user_devices:
                try:
                    message = {
                        "type": "device_update",
                        "device_id": device.get("ieee_address") or device.get("serial_number"),
                        "data": {
                            "friendly_name": device.get("friendly_name"),
                            "device_type": device.get("device_type"),
                            "last_seen": device.get("last_seen"),
                            "status": "active" if device.get("last_seen") else "inactive"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(message))
                    logger.info(f"Sent initial device state for device: {device.get('friendly_name')}")
                except Exception as send_error:
                    logger.error(f"Error sending device state for device {device.get('friendly_name')}: {send_error}")
        else:
            # Send empty state message
            try:
                message = {
                    "type": "connection_established",
                    "user_id": user_id,
                    "device_count": 0,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(message))
                logger.info(f"Sent connection established message for user: {user_id}")
            except Exception as send_error:
                logger.error(f"Error sending connection established message: {send_error}")

        # Keep connection alive and handle incoming messages
        logger.info(f"WebSocket connection established and ready for user: {user_id}")
        while True:
            try:
                message = await websocket.receive_text()
                logger.info(f"Received message from user {user_id}: {message[:100]}...")
                
                # Parse the message
                try:
                    message_data = json.loads(message)
                    message_type = message_data.get("type", "")
                    
                    if message_type == "heartbeat":
                        # Send heartbeat response
                        response = {
                            "type": "heartbeat_response",
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(response))
                        logger.debug(f"Sent heartbeat response to user: {user_id}")
                    else:
                        logger.info(f"Received unknown message type '{message_type}' from user: {user_id}")
                        
                except json.JSONDecodeError as json_error:
                    logger.warning(f"Invalid JSON received from user {user_id}: {json_error}")
                except Exception as parse_error:
                    logger.error(f"Error parsing message from user {user_id}: {parse_error}")
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected normally for user: {user_id}")
                break
            except Exception as receive_error:
                logger.error(f"Error receiving message from user {user_id}: {receive_error}")
                break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        # Clean up connection
        try:
            if user_id in app_state["websocket_connections"]:
                app_state["websocket_connections"][user_id].remove(websocket)
                if not app_state["websocket_connections"][user_id]:
                    del app_state["websocket_connections"][user_id]
                logger.info(f"WebSocket connection cleaned up for user: {user_id}")
        except Exception as cleanup_error:
            logger.error(f"Error cleaning up WebSocket connection for user {user_id}: {cleanup_error}")

@app.get("/health")
async def health_check():
    redis_status = "unknown"
    try:
        redis_db.conn.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    # Test database connection
    db_status = "unknown"
    try:
        # Simple test query
        test_result = pg_db.execute_query("SELECT 1 as test")
        db_status = "connected" if test_result else "no_data"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
        logger.error(f"Database health check failed: {e}")
    
    return {
        "status": "healthy",
        "mqtt_connected": mqtt_monitor.connected,
        "mqtt_broker": f"{settings.MQTT_BROKER}:{settings.MQTT_PORT}",
        "redis_status": redis_status,
        "redis_url": redis_db.redis_url.replace(redis_db.redis_url.split('@')[-1], '***') if '@' in redis_db.redis_url else redis_db.redis_url,
        "database_status": db_status,
        "devices": len(app_state["devices"]),
        "active_leaks": len(app_state["active_leaks"]),
        "websocket_connections": len(app_state["websocket_connections"])
    }

class TestNotificationRequest(BaseModel):
    device_token: str
    title: str = "Test Notification"
    body: str = "This is a test notification from your server"

@app.post("/test-notification")
async def test_notification(request: TestNotificationRequest):
    """Test APNs notification delivery"""
    try:
        from notifications.apns_service import apns_service
        
        success = await apns_service.send_notification(
            device_token=request.device_token,
            title=request.title,
            body=request.body,
            data={"type": "Alert", "timestamp": datetime.now().isoformat()},
            category="LEAK_ALERT"
        )
        
        return {
            "success": success,
            "device_token": request.device_token[:8] + "...",
            "message": "Notification sent successfully" if success else "Failed to send notification"
        }
        
    except ImportError as e:
        print(e)
        return {
            "success": False,
            "error": "APNs service not configured",
            "message": "Please configure APNs environment variables"
        }
    except Exception as e:
        logger.error(f"Test notification failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send test notification"
        }

# Adding new users
# TODO: Test e2e flow with rpi once set up
@app.post("/api/setup/generate", response_model=SetupResponse)
async def generate_location_setup(request: LocationSetupRequest):
    """Generate QR code and credentials for new location"""
    try:
        location_id = f"home_{uuid.uuid4().hex[:8]}"
        mqtt_password = secrets.token_urlsafe(16)
        
        await create_mqtt_user(location_id, mqtt_password)
        
        mqtt_config = {
            "location_id": location_id,
            "location_name": request.location_name,
            "mqtt": {
                "server": f"mqtt://{settings.MQTT_DOMAIN}:1883",
                "user": location_id,
                "password": mqtt_password,
                "base_topic": f"zigbee2mqtt/{location_id}",
                "client_id": f"{location_id}_zigbee2mqtt"
            },
            "api_endpoint": f"https://{settings.API_DOMAIN}",
            "setup_version": "1.0"
        }
        
        qr_code_base64 = generate_qr_code(mqtt_config)
        
        app_state["locations"][location_id] = {
            "name": request.location_name,
            "contact_info": request.contact_info,
            "created_at": datetime.now().isoformat(),
            "status": "pending_setup",
            "devices": {}
        }
        
        setup_instructions = f"""
Setup Instructions for {request.location_name}:

1. Power on the Senchi Home device
2. Connect it to WiFi using the device's hotspot
3. Scan this QR code with the device
4. The device will automatically configure itself
5. You'll see devices appear in your Senchi app within 5 minutes

Location ID: {location_id}
        """.strip()
        
        return SetupResponse(
            location_id=location_id,
            location_name=request.location_name,
            qr_code_base64=qr_code_base64,
            mqtt_config=mqtt_config,
            setup_instructions=setup_instructions
        )
        
    except Exception as e:
        logger.error(f"Setup generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Setup generation failed: {str(e)}")

async def create_mqtt_user(username: str, password: str):
    """Add user to MQTT broker"""
    try:
        result = subprocess.run([
            'mosquitto_passwd', '-b', 
            '/mosquitto/config/passwd',
            username, 
            password
        ], capture_output=True, text=True, check=True)
        
        subprocess.run(['pkill', '-HUP', 'mosquitto'], check=False)
        
        logger.info(f"Created MQTT user: {username}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create MQTT user {username}: {e}")
        raise

def generate_qr_code(config_data: dict) -> str:
    """Generate QR code containing setup configuration"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    config_json = json.dumps(config_data, separators=(',', ':'))
    qr.add_data(config_json)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

@app.get("/api/setup/locations")
async def list_locations():
    """List all configured locations"""
    return {
        "locations": app_state.get("locations", {}),
        "total": len(app_state.get("locations", {}))
    }

@app.delete("/api/setup/locations/{location_id}")
async def remove_location(location_id: str):
    """Remove a location and clean up MQTT user"""
    try:
        subprocess.run([
            'mosquitto_passwd', '-D',
            '/mosquitto/config/passwd',
            location_id
        ], check=True)
        
        subprocess.run(['pkill', '-HUP', 'mosquitto'], check=False)
        
        if location_id in app_state.get("locations", {}):
            del app_state["locations"][location_id]
        
        return {"status": "success", "message": f"Location {location_id} removed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove location: {str(e)}")

@app.post("/api/setup/confirm/{location_id}")
async def confirm_location_setup(location_id: str):
    """Called by RPi when setup is complete"""
    if location_id in app_state.get("locations", {}):
        app_state["locations"][location_id]["status"] = "active"
        app_state["locations"][location_id]["connected_at"] = datetime.now().isoformat()
        return {"status": "confirmed", "location_id": location_id}
    else:
        raise HTTPException(status_code=404, detail="Location not found")

def subscribe_to_new_topics_periodically(monitor, redis_db, interval=60):
    known_topics = set()
    while True:
        try:
            keys = redis_db.conn.keys("topic:*:jwts")
            for key in keys:
                topic = key.decode().split(":", 1)[1].rsplit(":", 1)[0]
                if topic not in known_topics:
                    monitor.client.subscribe(topic)
                    known_topics.add(topic)
                    logger.info(f"Subscribed to new topic: {topic}")
        except Exception as e:
            logger.error(f"Error subscribing to new topics: {e}")
        time.sleep(interval)

if __name__ == "__main__":

    # Extra debug logging for development
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )
    
    logging.getLogger().setLevel(logging.DEBUG)
    
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")