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
            
            # Note: This is republished each time a device is added/removed
            self.client.subscribe("zigbee2mqtt/bridge/health")
            self.client.subscribe("zigbee2mqtt/bridge/devices")
            self.client.subscribe("zigbee2mqtt/bridge/event")

            # Notify on successful device removal
            self.client.subscribe("zigbee2mqtt/bridge/response/device/remove")
            
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.connected = False

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
                    self.client.subscribe(f"zigbee2mqtt/{ieee_address}")
                    print(f"Subscribed to: {ieee_address}")
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

    
