import json
import sys
import queue
import time
import asyncio
from typing import Any, Dict, List
from datetime import datetime
import logging
import threading

from fastapi import WebSocket
import paho.mqtt.client as mqtt
import pandas as pd

from monitor.config import settings
from monitor.models import Device, LandlordNotification


logger = logging.getLogger(__name__)


class Monitor:
    def __init__(self, initial_app_state: dict, db: pd.DataFrame):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        self.message_queue = queue.Queue()
        self.loop = None

        # TODO: Can this just be defined here?
        self.app_state = initial_app_state

        # TODO: Update this once we have a proper database
        self.db = db

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: dict,
        rc: int,
    ) -> None:
        if rc == 0:
            self.connected = True
            logger.info(f"Successfully connected to MQTT broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            logger.info(f"MQTT client ID: {client._client_id}")
            
            # Subscribe to topics for all known device serials
            self._subscribe_to_device_topics()
            
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.connected = False
    
    def _subscribe_to_device_topics(self):
        """Subscribe to MQTT topics for all known device serials"""
        try:
            # Get all JWT tokens from Redis to find device serials
            if hasattr(self, 'app_state') and 'redis_db' in self.app_state:
                redis_db = self.app_state['redis_db']
            else:
                # Fallback to global redis_db
                from rdsdb.rdsdb import RedisDB
                redis_db = RedisDB()
            
            # Check if Redis is connected
            if not redis_db.conn:
                logger.warning("Redis not connected, attempting to connect...")
                print("Redis not connected, attempting to connect...")
                try:
                    redis_db.connect()
                    print("Redis connection successful")
                except Exception as e:
                    logger.error(f"Failed to connect to Redis: {e}")
                    print(f"Failed to connect to Redis: {e}")
                    logger.warning("Subscribing to default topics only")
                    self._subscribe_to_default_topics()
                    return
            
            # Get all JWT keys
            try:
                jwt_keys = redis_db.conn.keys("jwt:*")
                device_serials = set()
                print(f"JWT keys found: {len(jwt_keys)}")
                
                if not jwt_keys:
                    print("No JWT keys found in Redis")
                    logger.warning("No JWT keys found in Redis, subscribing to default topics")
                    self._subscribe_to_default_topics()
                    return
                
                for key in jwt_keys:
                    try:
                        # Get the JWT token from the key
                        jwt_token = key.decode().split(":", 1)[1]
                        print(f"Processing JWT token: {jwt_token[:50]}...")
                        
                        # Get the JWT data
                        jwt_data = redis_db.get_key(f"jwt:{jwt_token}")
                        if jwt_data:
                            import json
                            data = json.loads(jwt_data)
                            print(f"JWT data: {data}")
                            
                            # Try to get device_serial from different possible fields
                            device_serial = None
                            if 'device_serial' in data:
                                device_serial = data['device_serial']
                            elif 'location_id' in data:
                                # Extract device serial from location_id (e.g., "rpi-zigbee-nrjrjr" -> "nrjrjr")
                                location_id = data['location_id']
                                if location_id.startswith('rpi-zigbee-'):
                                    device_serial = location_id.replace('rpi-zigbee-', '')
                                else:
                                    device_serial = location_id
                            
                            if device_serial:
                                device_serials.add(device_serial)
                                print(f"Added device serial: {device_serial}")
                            else:
                                print(f"No device serial found in JWT data: {data}")
                    except Exception as e:
                        logger.warning(f"Error processing JWT key {key}: {e}")
                        print(f"Error processing JWT key {key}: {e}")
                        continue
                
                # Subscribe to topics for each device serial
                for device_serial in device_serials:
                    # Use the correct topic format: zigbee2mqtt/senchi-{device_serial}/*
                    base_topic = f"zigbee2mqtt/senchi-{device_serial}"
                    
                    topics = [
                        f"{base_topic}/bridge/health",
                        f"{base_topic}/bridge/devices", 
                        f"{base_topic}/bridge/event",
                        f"{base_topic}/bridge/response/device/remove",
                    ]
                    
                    print(f"Subscribing to topics for device serial: {device_serial}")
                    for topic in topics:
                        try:
                            self.client.subscribe(topic)
                            logger.info(f"Subscribed to topic: {topic}")
                            print(f"✅ Subscribed to topic: {topic}")
                        except Exception as e:
                            logger.error(f"Failed to subscribe to {topic}: {e}")
                            print(f"❌ Failed to subscribe to {topic}: {e}")
                
                if not device_serials:
                    logger.warning("No device serials found in Redis, subscribing to default topics")
                    print("No device serials found in Redis, subscribing to default topics")
                    self._subscribe_to_default_topics()
                    
            except Exception as e:
                logger.error(f"Error accessing Redis keys: {e}")
                logger.warning("Subscribing to default topics due to Redis error")
                self._subscribe_to_default_topics()
                        
        except Exception as e:
            logger.error(f"Error subscribing to device topics: {e}")
            logger.warning("Subscribing to default topics due to error")
            self._subscribe_to_default_topics()

    def _subscribe_to_default_topics(self):
        """Subscribe to default topics for testing when Redis is unavailable"""
        default_topics = [
            "zigbee2mqtt/senchi-SNH2025001/bridge/health",
            "zigbee2mqtt/senchi-SNH2025001/bridge/devices",
            "zigbee2mqtt/senchi-SNH2025001/bridge/event",
            "zigbee2mqtt/senchi-SNH2025001/bridge/response/device/remove",
        ]
        for topic in default_topics:
            try:
                self.client.subscribe(topic)
                logger.info(f"Subscribed to default topic: {topic}")
            except Exception as e:
                logger.error(f"Failed to subscribe to default topic {topic}: {e}")

    def on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
    ):
        self.connected = False

    def on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ):
        topic = msg.topic
        # Some MQTT messages might have empty or non-JSON payloads
        try:
            payload_str = msg.payload.decode("utf-8")
            if not payload_str.strip():
                return
                
            payload = json.loads(payload_str)

            if "bridge/response/device/remove" in topic:
                logger.info(f"Device removed: {payload['data']['id']}")

            elif "bridge/devices" in topic or "bridge/event" in topic:
                asyncio.run_coroutine_threadsafe(
                    self.handle_device_list(payload), 
                    self.loop
                )
                return
            
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logging.error(f"Error decoding MQTT message: {e}")
            return

        ieee_address = topic.split("/")[-1]
        if isinstance(payload, dict):
            if self.loop and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self.handle_device_update(ieee_address, payload), 
                    self.loop
                )
        # --- Route notification by topic ---
        self.route_notification_by_topic(topic, payload)

    async def handle_device_list(self, devices: List[Dict]):
        i = 0
        print(f"There are {len(devices)} devices")
        for device_data in devices:
            i += 1
            print(f"Processing device {i}: {device_data.get('ieee_address', 'NO_IEEE')}")
            if device_data.get("type") == "Coordinator" or \
                not device_data.get("ieee_address"):
                print(f"Skipping coordinator")
                continue
            # elif device_data.get("ieee_address") in self.app_state["devices"]:
            #     continue
            print(f"About to create Device object for {device_data.get('ieee_address')}")
            try:
                curr = Device(**device_data)
            except Exception as e:
                # NOTE: Errors are sometimes "swallowed" by the asyncio loop
                print(f"Error creating device: {e}")
                logger.error(f"Error creating device: {e}")
                continue
            
            ieee_address = curr.ieee_address
            print(f"Checking if {ieee_address} exists in app_state")
            
            if ieee_address not in self.app_state["devices"]:
                print(f"Adding new device: {ieee_address}")
                self.app_state["devices"][ieee_address] = curr
                try:
                    # Subscribe to device updates using the correct topic format
                    # We need to determine which device serial this belongs to
                    # For now, use the default device serial
                    device_serial = "SNH2025001"  # TODO: Get from context
                    self.client.subscribe(f"zigbee2mqtt/senchi-{device_serial}/{ieee_address}")
                    print(f"Subscribed to: zigbee2mqtt/senchi-{device_serial}/{ieee_address}")
                except Exception as e:
                    print(f"Error subscribing to device: {e}")
                    logger.error(f"Error subscribing to device: {e}")
                
                logger.info(f"Added device: {ieee_address}")
            else:
                if ieee_address in self.app_state["devices"]:
                    existing_device = self.app_state["devices"][ieee_address]
                    for field, value in curr.dict(exclude_unset=True).items():
                        if value is not None:
                            setattr(existing_device, field, value)
                    logger.info(f"Updated device: {ieee_address}")
        print(f"Added {i} devices")

    async def handle_device_update(self, ieee_address: str, payload: Dict) -> bool:
        device = self.app_state["devices"][ieee_address]
        logger.info(f'Device: {device}')
        device.status = payload
        device.last_seen = datetime.now()
        print(f"Payload: {payload}")
        
        try:
            # Store event in database
            # if not self.store_device_event(ieee_address, "state_update", payload):
            #     return
            
            # Check for notification triggers
            # await self.check_notification_triggers(ieee_address, payload)
            
            # Broadcast to WebSocket clients
            await self.broadcast_device_update(ieee_address, payload)

            return True
        except Exception as e:
            logger.error(f"Error handling device update: {e}")
            return False

    def store_device_event(self, device_id: str, event_type: str, data: Dict) -> bool:
        self.db["notifications"].loc[device_id, event_type] = data


    async def check_notification_triggers(self, device_id: str, payload: Dict):
        """Check if this update should trigger notifications"""
        
        device_name = self.app_state["devices"][device_id]["name"]
        
        # Water leak detection
        water_leak = payload.get("water_leak")
        if water_leak is True and device_id not in self.app_state["active_leaks"]:
            self.app_state["active_leaks"].add(device_id)
            
            message = f"Leak detected:\nDevice: {device_name}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            await self.send_notification(device_id, message, "leak_alert", priority="high")
            
            logging.warning(f"leak alert: {device_name}")
            
        elif water_leak is False and device_id in self.app_state["active_leaks"]:
            # Leak cleared
            self.app_state["active_leaks"].remove(device_id)
            
            message = f"Leak cleared on {device_name}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            await self.send_notification(device_id, message, "leak_cleared", priority="normal")
            
            logging.info(f"Leak cleared: {device_name}")
        
        low_battery = payload.get("battery")
        if low_battery is not None and not low_battery:
            if not self.battery_alert_recently_sent(device_id):
                message = f"Low battery warning\n\nDevice: {device_name}\nBattery: {low_battery}%"
                await self.send_notification(device_id, message, "low_battery", priority="normal")

    def battery_alert_recently_sent(self, device_id: str) -> bool:
        # TODO: Implement this once db is implemented
        return True
    
    async def send_notification(
        self, device_id: str, message: str, notification_type: str, priority: str
    ) -> bool:
        if not self.app_state["notification_config"] or \
            not self.app_state["notification_config"].get("enabled", True):
            return False
        
        payload = LandlordNotification(
            target_id=device_id,
            notification_type=notification_type,
            priority=priority,
            message=message,
            sent_at=datetime.now(),
        )
        logger.info(f"Notification payload: {payload}")
        logger.info(f"Sending notification: {message}")
        
        return True

    async def broadcast_device_update(self, device_id: str, payload: Dict):
        message = {
            "type": "device_update",
            "device_id": device_id,
            "data": payload,
            "timestamp": datetime.now().isoformat()
        }
        
        # Remove disconnected clients
        disconnected = []
        for websocket in self.app_state["websocket_connections"]:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(websocket)
        
        for client in disconnected:
            self.app_state["websocket_connections"].remove(client)

    def start(self):

        try:
            if hasattr(settings, 'MQTT_USERNAME') and hasattr(settings, 'MQTT_PASSWORD'):
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

            logging.debug(f"Attempting to connect to MQTT broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            
            # Start the network loop in a background thread
            self.client.loop_start()
            
            # Connect to broker
            result = self.client.connect(
                settings.MQTT_BROKER, 
                settings.MQTT_PORT,
                60
            )
            time.sleep(2)
            
            if result != 0:
                logging.error(f"Failed to connect to MQTT broker, result code: {result}")
                self.client.loop_stop()
                return
                
            logging.debug("MQTT Monitor started...")
            
        except Exception as e:
            logging.error(f"MQTT monitor error: {e}")
            self.client.loop_stop()
    
    def stop(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

    def route_notification_by_topic(self, topic, payload):
        # Find all JWTs associated with this topic
        jwt_key = f"topic:{topic}:jwts"
        
        # Try to get Redis connection from app_state first
        redis_db = None
        if "redis_db" in self.app_state:
            redis_db = self.app_state["redis_db"]
        
        # If not in app_state, try to get global redis_db
        if not redis_db:
            try:
                # TODO: Remove this, temp fix
                from rdsdb.rdsdb import RedisDB
                redis_db = RedisDB()
                # Try to connect if not already connected
                if not redis_db.conn:
                    redis_db.connect()
            except Exception as e:
                logger.warning(f"Could not get Redis connection for topic routing: {e}")
                return
        
        # Get JWT data if Redis is available
        jwt_data = None
        if redis_db and redis_db.conn:
            try:
                jwt_data = redis_db.get_key(jwt_key)
            except Exception as e:
                logger.warning(f"Error getting JWT data for topic {topic}: {e}")
                return
        
        if not jwt_data:
            logger.info(f"No JWTs found for topic {topic}")
            return
            
        try:
            jwt_list = jwt_data.decode().split(",")
            for jwt_token in jwt_list:
                logger.info(f"Would route notification to JWT: {jwt_token} for topic: {topic}")
                # Here you can send a notification to the user/device associated with this JWT
                # For example, via WebSocket, push, etc.
                # Example: self.send_websocket_notification(jwt_token, payload)
        except Exception as e:
            logger.error(f"Error processing JWT data for topic {topic}: {e}")

    
