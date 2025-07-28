import json
import sys
import queue
import time
import asyncio
from typing import Any, Dict, List, Union
from datetime import datetime
import logging
import threading

from fastapi import WebSocket
import paho.mqtt.client as mqtt
import pandas as pd

from monitor.config import settings
from monitor.models import Device, LandlordNotification
from maindb.pg import PostgresDB

logger = logging.getLogger(__name__)


class Monitor:
    def __init__(self, initial_app_state: dict, db: Union[PostgresDB, pd.DataFrame]):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        self.message_queue = queue.Queue()
        self.loop = None
        self.current_device_serial = None

        # TODO: Can this just be defined here?
        self.app_state = initial_app_state

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
            
            # Restore devices from database and subscribe to their topics
            self._restore_devices_from_database()
            
            # Request device list from bridge to restore device state after a short delay
            # This ensures the connection is fully established
            def delayed_request():
                time.sleep(2)  # Wait 2 seconds for connection to stabilize
                self._request_device_list()
            
            threading.Thread(target=delayed_request, daemon=True).start()
            
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.connected = False
    
    def _subscribe_to_device_topics(self):
        """Subscribe to MQTT topics for all known device serials"""
        try:
            if isinstance(self.db, pd.DataFrame):
                device_serials = self.db.index.tolist()
            else:
                device_serials = self.db.get_device_serials()
                
                # Subscribe to topics for each device serial
                for device_serial in device_serials:
                    # Use the correct topic format: zigbee2mqtt/senchi-{device_serial}/*
                    base_topic = f"zigbee2mqtt/senchi-{device_serial['serial_number']}"
                    
                    topics = [
                        f"{base_topic}/bridge/health",
                        f"{base_topic}/bridge/devices", 
                        f"{base_topic}/bridge/event",
                        f"{base_topic}/bridge/response/device/remove",
                    ]
                    
                    for topic in topics:
                        try:
                            self.client.subscribe(topic)
                            print(f"Subscribed to topic: {topic}")
                            logger.info(f"Subscribed to topic: {topic}")
                        except Exception as e:
                            logger.error(f"Failed to subscribe to {topic}: {e}")
                
                print(f"Subscribed to {len(device_serials)} topics")
                if not device_serials:
                    logger.warning("No device serials found in Redis, subscribing to default topics")
                    print("No device serials found in Redis, subscribing to default topics")
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

    def _request_device_list(self):
        """Request the current device list from the bridge to restore device state"""
        try:
            # Get device serials from Redis or use default
            device_serials = self._get_device_serials()
            
            for device_serial in device_serials:
                # Request device list from bridge
                topic = f"zigbee2mqtt/senchi-{device_serial}/bridge/request/devices"
                payload = json.dumps({})
                
                logger.info(f"Requesting device list from bridge: {topic}")
                result = self.client.publish(topic, payload)
                
                if result.rc == 0:
                    logger.info(f"Device list request sent successfully to {topic}")
                else:
                    logger.error(f"Failed to send device list request to {topic}: rc={result.rc}")
                    
        except Exception as e:
            logger.error(f"Error requesting device list: {e}")
    
    def _extract_device_serial_from_topic(self):
        """Extract device serial from the last bridge/devices topic received"""
        if hasattr(self, 'current_device_serial') and self.current_device_serial:
            return self.current_device_serial
        # Default fallback
        return "SNH2025001"
    
    def _store_device_mapping(self, device_serial: str, device: Device):
        """Store device mapping in database"""
        try:
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available for device mapping")
                return
            
            # Store the original device type for reference, but use the enum-compatible type for the Device object
            original_device_type = getattr(device, 'original_device_type', device.type)
            
            pg_db.upsert_device_mapping(
                device_serial=device_serial,
                ieee_address=device.ieee_address,
                friendly_name=device.friendly_name,
                device_type=original_device_type,  # Store the original type (e.g., 'leak_sensor')
                model=device.model,
                manufacturer=device.manufacturer
            )
            logger.info(f"Stored device mapping: {device_serial} -> {device.ieee_address}")
            
        except Exception as e:
            logger.error(f"Error storing device mapping: {e}")
    
    def _remove_device_mapping(self, device_serial: str, ieee_address: str):
        """Remove device mapping from database"""
        try:
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available for device mapping removal")
                return
            
            pg_db.remove_device_mapping(device_serial, ieee_address)
            logger.info(f"Removed device mapping: {device_serial} -> {ieee_address}")
            
        except Exception as e:
            logger.error(f"Error removing device mapping: {e}")
    
    def _restore_devices_from_database(self):
        """Restore devices from database and subscribe to their topics"""
        try:
            # Get PostgreSQL database from app_state
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available in app_state")
                return
            
            # Get device serials from Redis or use default
            device_serials = self._get_device_serials()
            
            for device_serial in device_serials:
                logger.info(f"Restoring devices for device serial: {device_serial}")
                
                # Get devices from database for this serial
                devices = pg_db.get_devices_by_serial(device_serial)
                
                for device_data in devices:
                    ieee_address = device_data['ieee_address']
                    friendly_name = device_data['friendly_name']
                    
                    # Create a minimal Device object for restoration
                    # Use the device_type directly since it's already in the DeviceType enum
                    device_type = device_data.get('device_type', 'EndDevice')
                    
                    device_info = {
                        'ieee_address': ieee_address,
                        'friendly_name': friendly_name,
                        'type': device_type,
                        'model': device_data.get('model', ''),
                        'manufacturer': device_data.get('manufacturer', ''),
                        'status': {},
                        'last_seen': device_data.get('last_seen')
                    }
                    
                    try:
                        device = Device(**device_info)
                        self.app_state["devices"][ieee_address] = device
                        
                        # Subscribe to device topic
                        self.client.subscribe(f"zigbee2mqtt/senchi-{device_serial}/{ieee_address}")
                        logger.info(f"Restored device and subscribed to: zigbee2mqtt/senchi-{device_serial}/{ieee_address}")
                        
                    except Exception as e:
                        logger.error(f"Error restoring device {ieee_address}: {e}")
                
                logger.info(f"Restored {len(devices)} devices for device serial: {device_serial}")
                
        except Exception as e:
            logger.error(f"Error restoring devices from database: {e}")
    
    def _get_device_serials(self):
        """Get list of device serials from Redis or return default"""
        device_serials = set()
        
        try:
            # Try to get from Redis
            if hasattr(self, 'app_state') and 'redis_db' in self.app_state:
                redis_db = self.app_state['redis_db']
                
                if redis_db.conn:
                    jwt_keys = redis_db.conn.keys("jwt:*")
                    
                    for key in jwt_keys:
                        key_str = key.decode()
                        if key_str.endswith(':topic'):
                            continue
                        
                        jwt_token = key_str.split(":", 1)[1]
                        jwt_data = redis_db.get_key(f"jwt:{jwt_token}")
                        
                        if jwt_data:
                            if isinstance(jwt_data, bytes):
                                jwt_data = jwt_data.decode('utf-8')
                            
                            try:
                                data = json.loads(jwt_data)
                                device_serial = None
                                
                                if 'device_serial' in data:
                                    device_serial = data['device_serial']
                                elif 'location_id' in data:
                                    location_id = data['location_id']
                                    if location_id.startswith('rpi-zigbee-'):
                                        device_serial = location_id.replace('rpi-zigbee-', '')
                                    else:
                                        device_serial = location_id
                                
                                if device_serial:
                                    device_serials.add(device_serial)
                                    
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.warning(f"Error getting device serials from Redis: {e}")
        
        # If no device serials found, use default
        if not device_serials:
            device_serials.add("SNH2025001")
            logger.info("Using default device serial: SNH2025001")
        
        return device_serials

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
                
                # Remove device from database
                device_serial = self._extract_device_serial_from_topic()
                self._remove_device_mapping(device_serial, payload['data']['id'])
                
                # Log device removal event
                asyncio.run_coroutine_threadsafe(
                    self.log_device_event(payload['data']['id'], {"event": "device_removed", "data": payload}),
                    self.loop
                )

            elif "bridge/devices" in topic:
                # Extract device serial from topic for device subscriptions
                device_serial = topic.split("/")[1].replace("senchi-", "")
                self.current_device_serial = device_serial
                logger.info(f"Processing device list for device serial: {device_serial}")
                
                asyncio.run_coroutine_threadsafe(
                    self.handle_device_list(payload), 
                    self.loop
                )
                return
            elif "bridge/event" in topic:
                # Log bridge events
                asyncio.run_coroutine_threadsafe(
                    self.log_bridge_event(payload),
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
                # Handle unknown device types by mapping them to a valid enum value
                device_data_copy = device_data.copy()
                if device_data_copy.get('type') == 'Unknown':
                    device_data_copy['type'] = 'EndDevice'  # Default unknown devices to EndDevice
                    logger.info(f"Mapping unknown device type to EndDevice for {device_data.get('ieee_address')}")
                
                curr = Device(**device_data_copy)
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
                
                # Store device mapping in database
                device_serial = self._extract_device_serial_from_topic()
                self._store_device_mapping(device_serial, curr)
                
                try:
                    # Subscribe to device updates using the correct topic format
                    # Extract device serial from the topic that sent the device list
                    self.client.subscribe(f"zigbee2mqtt/senchi-{device_serial}/{ieee_address}")
                    print(f"Subscribed to: zigbee2mqtt/senchi-{device_serial}/{ieee_address}")
                except Exception as e:
                    print(f"Error subscribing to device: {e}")
                    logger.error(f"Error subscribing to device: {e}")
                
                logger.info(f"Added device: {ieee_address}")
                
                # Log new device event to PostgreSQL
                asyncio.run_coroutine_threadsafe(
                    self.log_device_event(ieee_address, {"event": "device_added", "device_data": curr.dict()}),
                    self.loop
                )
            else:
                if ieee_address in self.app_state["devices"]:
                    existing_device = self.app_state["devices"][ieee_address]
                    for field, value in curr.dict(exclude_unset=True).items():
                        if value is not None:
                            setattr(existing_device, field, value)
                    logger.info(f"Updated device: {ieee_address}")
                    
                    # Log device update event to PostgreSQL
                    asyncio.run_coroutine_threadsafe(
                        self.log_device_event(ieee_address, {"event": "device_updated", "device_data": curr.dict()}),
                        self.loop
                    )
        print(f"Added {i} devices")

    async def handle_device_update(self, ieee_address: str, payload: Dict) -> bool:
        device = self.app_state["devices"][ieee_address]
        logger.info(f'Device: {device}')
        device.status = payload
        device.last_seen = datetime.now()
        print(f"Payload: {payload}")
        
        try:
            # Log device event to PostgreSQL
            await self.log_device_event(ieee_address, payload)
            
            # Log sensor events (leaks, battery warnings, etc.)
            await self.log_sensor_event(ieee_address, payload)
            
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

    async def log_device_event(self, device_id: str, payload: Dict) -> bool:
        """Log device event to PostgreSQL database.
        
        Args:
            device_id: The device IEEE address
            payload: The device payload/status data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get PostgreSQL database from app_state
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available in app_state")
                return False
            
            # Get device info
            device = self.app_state["devices"].get(device_id)
            device_name = device.friendly_name if device else device_id
            
            # Determine event type from payload
            event_type = 'device_update'
            if 'event' in payload:
                event_type = payload['event']
            
            # Insert event into PostgreSQL
            query = """
            INSERT INTO events (device, event_type, event_time, event_location, time_to_stop)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                device_name,
                event_type,
                datetime.now(),
                'unknown',  # Could be enhanced to get from device config
                None  # Not applicable for device updates
            )
            
            row_count = pg_db.execute_insert(query, params)
            
            if row_count > 0:
                logger.info(f"Successfully logged device event to PostgreSQL: {device_id}")
            else:
                logger.error(f"Failed to log device event to PostgreSQL: {device_id}")
            
            return row_count > 0
            
        except Exception as e:
            logger.error(f"Error logging device event to PostgreSQL: {e}")
            return False

    # TODO: Refine the event logging
    async def log_sensor_event(self, device_id: str, payload: Dict) -> bool:
        """Log sensor events like leaks, battery warnings, etc. to PostgreSQL database.
        
        Args:
            device_id: The device IEEE address
            payload: The device payload/status data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get PostgreSQL database from app_state
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available in app_state")
                return False
            
            # Get device info
            device = self.app_state["devices"].get(device_id)
            device_name = device.friendly_name if device else device_id
            
            events_to_log = []
            
            # Check for water leak detection
            water_leak = payload.get('water_leak')
            if water_leak is True:
                events_to_log.append(('water_leak_detected', None))
            elif water_leak is False:
                events_to_log.append(('water_leak_cleared', None))
            
            # Check for battery warnings
            battery = payload.get('battery')
            battery_low = payload.get('battery_low')
            if battery is not None and battery < 20:
                events_to_log.append(('low_battery', battery))
            elif battery_low is True:
                events_to_log.append(('battery_low', battery))
            
            # Check for power outages
            power_outage_count = payload.get('power_outage_count')
            if power_outage_count is not None and power_outage_count > 0:
                events_to_log.append(('power_outage', power_outage_count))
            
            # Check for device temperature warnings
            device_temperature = payload.get('device_temperature')
            if device_temperature is not None and device_temperature > 50:
                events_to_log.append(('high_temperature', device_temperature))
            
            # Check for voltage issues
            voltage = payload.get('voltage')
            if voltage is not None and voltage < 2800:  # Low voltage threshold
                events_to_log.append(('low_voltage', voltage))
            
            # Check for trigger events (motion, etc.)
            trigger_count = payload.get('trigger_count')
            if trigger_count is not None and trigger_count > 0:
                events_to_log.append(('trigger_event', trigger_count))
            
            # Log all detected events
            for event_type, value in events_to_log:
                query = """
                INSERT INTO events (device, event_type, event_time, event_location, time_to_stop)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (
                    device_name,
                    event_type,
                    datetime.now(),
                    'unknown',  # Could be enhanced to get from device config
                    value
                )
                
                row_count = pg_db.execute_insert(query, params)
                
                if row_count > 0:
                    logger.info(f"Successfully logged sensor event to PostgreSQL: {device_id} - {event_type}")
                else:
                    logger.error(f"Failed to log sensor event to PostgreSQL: {device_id} - {event_type}")
            
            return len(events_to_log) > 0
            
        except Exception as e:
            logger.error(f"Error logging sensor event to PostgreSQL: {e}")
            return False

    # TODO: Move to separate db
    async def log_bridge_event(self, payload: Dict) -> bool:
        """Log bridge event to PostgreSQL database.
        
        Args:
            payload: The bridge event payload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get PostgreSQL database from app_state
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available in app_state")
                return False
            
            # Extract event info from payload
            event_type = payload.get('type', 'unknown')
            data = payload.get('data', {})
            
            # Insert bridge event into PostgreSQL
            query = """
            INSERT INTO events (device, event_type, event_time, event_location, time_to_stop)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                data.get('friendly_name', 'bridge'),
                f"bridge_{event_type}",
                datetime.now(),
                'bridge',
                None
            )
            
            row_count = pg_db.execute_insert(query, params)
            
            if row_count > 0:
                logger.info(f"Successfully logged bridge event to PostgreSQL: {event_type}")
            else:
                logger.error(f"Failed to log bridge event to PostgreSQL: {event_type}")
            
            return row_count > 0
            
        except Exception as e:
            logger.error(f"Error logging bridge event to PostgreSQL: {e}")
            return False

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
        """Broadcast device updates to connected WebSocket clients for the device owner"""
        try:
            # Get device info to find the owner
            device = self.app_state["devices"].get(device_id)
            if not device:
                logger.warning(f"Device {device_id} not found for broadcast")
                return
            
            # Get device owner from database
            pg_db = self.app_state.get("pg_db")
            if not pg_db:
                logger.warning("PostgreSQL database not available for device owner lookup")
                return
            
            # Find the device owner by looking up the device in the database
            # This assumes the device_id is the ieee_address
            owner_query = """
            SELECT DISTINCT d.owner_user_id 
            FROM zb_devices d
            JOIN device_mappings dm ON d.serial_number = dm.device_serial
            WHERE dm.ieee_address = %s
            """
            
            owner_result = pg_db.execute_query(owner_query, (device_id,))
            if not owner_result:
                logger.warning(f"No owner found for device {device_id}")
                return
            
            owner_user_id = owner_result[0][0]
            
            # Create the message
            message = {
                "type": "device_update",
                "device_id": device_id,
                "data": {
                    "friendly_name": getattr(device, 'friendly_name', None),
                    "device_type": getattr(device, 'type', None),
                    "last_seen": getattr(device, 'last_seen', None),
                    "status": "active",
                    "battery": payload.get("battery"),
                    "water_leak": payload.get("water_leak"),
                    "linkquality": payload.get("linkquality"),
                    **payload  # Include all other payload data
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected WebSocket clients for this user
            if owner_user_id in self.app_state.get("websocket_connections", {}):
                disconnected_clients = []
                for websocket in self.app_state["websocket_connections"][owner_user_id]:
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Failed to send device update to WebSocket: {e}")
                        disconnected_clients.append(websocket)
                
                # Clean up disconnected clients
                for websocket in disconnected_clients:
                    try:
                        self.app_state["websocket_connections"][owner_user_id].remove(websocket)
                    except ValueError:
                        pass  # Already removed
                
                # Remove empty user connections
                if not self.app_state["websocket_connections"][owner_user_id]:
                    del self.app_state["websocket_connections"][owner_user_id]
                    
        except Exception as e:
            logger.error(f"Error broadcasting device update for {device_id}: {e}")

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

    
