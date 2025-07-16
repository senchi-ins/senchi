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
from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect, Depends
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
)
from monitor.zbm import Monitor
from monitor.utils import get_all_model_fields
from notifications.noti import NotificationRouter
from rdsdb.rdsdb import RedisDB

logger = logging.getLogger(__name__)

app_state = {
    "devices": {},
    "websocket_connections": [],
    "mqtt_client": None,
    "notification_config": None,
    "active_leaks": set(),
    "notification_queue": asyncio.Queue()
}

def init_db():
    """
    Initialize the database connection.

    Note: Currently uses pd.df and writed to a csv file.
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

# Add Redis database to app_state so Monitor can access it
app_state["redis_db"] = redis_db


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


@app.get("/devices")
async def get_devices():
    """Get all devices"""
    return list(app_state["devices"].values())


@app.post("/api/auth/setup", response_model=TokenResponse)
async def setup_device_auth(request: TokenRequest):
    """Generate JWT token during device setup"""
    return await notification_router.create_user_token(
        device_serial=request.device_serial,
        push_token=request.push_token,
        email=request.email  # Add email parameter
    )

@app.post("/api/auth/push-token")
async def update_push_token(
    push_token: str,
    current_user: dict = Depends(get_current_user)
):
    """Update user's push notification token"""
    await notification_router.update_push_token(current_user["jwt_token"], push_token)
    return {"message": "Push token updated successfully"}

@app.get("/api/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if token is valid"""
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "location_id": current_user["location_id"],
        "device_serial": current_user.get("device_serial", ""),
        "expires_at": current_user["exp"]
    }

class LoginRequest(BaseModel):
    email: str

@app.post("/api/auth/login")
async def login_with_email(request: LoginRequest):
    """Login with email to retrieve stored token"""
    try:
        email = request.email
        # Get token from Redis using email
        token = redis_db.get_key(f"email:{email}")
        print(f"Token for email {email}: {token}")
        
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
    print(f"Setting key: {request.key} with value: {request.value[:50]}... and ttl: {request.ttl}")
    logger.info(f"Setting key: {request.key} with ttl: {request.ttl}")
    redis_db.set_key(request.key, request.value, request.ttl)
    return {"message": "Key set successfully"}

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
    print(f"Full user token data: {current_user}")
    
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
    

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app_state["websocket_connections"].append(websocket)
    
    try:
        for device_id, device in app_state["devices"].items():
            message = {
                "type": "device_update",
                "device_id": device_id,
                "data": device.status,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(message))
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        app_state["websocket_connections"].remove(websocket)

@app.get("/health")
async def health_check():
    redis_status = "unknown"
    try:
        redis_db.conn.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    return {
        "status": "healthy",
        "mqtt_connected": mqtt_monitor.connected,
        "mqtt_broker": f"{settings.MQTT_BROKER}:{settings.MQTT_PORT}",
        "redis_status": redis_status,
        "redis_url": redis_db.redis_url.replace(redis_db.redis_url.split('@')[-1], '***') if '@' in redis_db.redis_url else redis_db.redis_url,
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
            data={"type": "test", "timestamp": datetime.now().isoformat()},
            category="TEST"
        )
        
        return {
            "success": success,
            "device_token": request.device_token[:8] + "...",
            "message": "Notification sent successfully" if success else "Failed to send notification"
        }
        
    except ImportError:
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