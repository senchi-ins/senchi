#!/usr/bin/env python3
"""
WoSenW Handshake Test Script

This script helps test the handshake functionality with WoSenW leak detector devices.
It can be used to verify the handshake sequence and debug connection issues.
"""

import asyncio
import logging
from bleak import BleakClient, BleakScanner
from enum import Enum, auto
from typing import Any, Callable, NamedTuple
from core.iot.wifi.decode_bytearray import decode_wosenw_status_packet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# WoSenW Device Configuration
WOSENW_SERVICE_UUID = "CBA20D00-224D-11E6-9FB8-0002A5D5C51B"
WOSENW_NOTIFY_UUID = "CBA20003-224D-11E6-9FB8-0002A5D5C51B"
WOSENW_WRITE_UUID = "CBA20002-224D-11E6-9FB8-0002A5D5C51B"

# Handshake sequences (matching iOS app)
HANDSHAKE_SEQUENCES = {
    "WoSenW": [
        bytes([0x01, 0x00]),  # Initiate pairing
        bytes([0x02, 0x01]),  # Confirm pairing
        bytes([0x03, 0x00]),  # Request device info
        bytes([0x04, 0x01]),  # Enable notifications
        bytes([0x05, 0x00])   # Complete handshake
    ],
    "Generic": [
        bytes([0xAA, 0x55]),  # Standard BLE handshake
        bytes([0x55, 0xAA]),  # Response
        bytes([0x01, 0x01])   # Enable notifications
    ]
}

class EventType(Enum):
    CONNECTED = auto()
    CHAR_XXXX = auto()


class Event(NamedTuple):
    type: EventType
    payload: Any

class Observer:
    def __init__(self):
        self.connected = False
        self.disconnected = False

    def on_next(self, value):
        self.connected = True
        self.disconnected = False

    def on_completed(self):
        self.connected = False
        self.disconnected = True
    
    def on_error(self, error):
        self.connected = False
        self.disconnected = True

class WoSenWHandshakeTester:
    def __init__(self):
        self.client = None
        self.handshake_completed = False
        self.pairing_finalized = False
        self.current_step = 0
        self.received_responses = []

    async def monitor_connection(
            self,
            client: BleakClient, 
            observer: Observer, 
            disconnect_event: asyncio.Event
        ):

        try:
            def on_disconnect():
                disconnect_event.set()
            
            client.set_disconnected_callback(on_disconnect)

            def on_notify_received(_, data):
                observer.on_next(Event(EventType.CHAR_XXXX, data))

            async with client:
                await client.start_notify("XXXX", on_notify_received)
                observer.on_next(Event(EventType.CONNECTED, None))
                await disconnect_event.wait()

            observer.on_completed()
        except Exception as e:
            observer.on_error(e)

    def subscribe(self, address: str, observer: Observer) -> Callable[[], None]:
        client = BleakClient(address)
        disconnect_event = asyncio.Event()
        asyncio.ensure_future(self.monitor_connection(client, observer, disconnect_event))

        return disconnect_event.set
        
    async def scan_for_devices(self):
        """Scan specifically for WoSenW devices"""
        all_devices = []
        
        devices = await BleakScanner.discover(timeout=10.0)
        all_devices.extend(devices)
        
        devices_with_services = await BleakScanner.discover(
            timeout=5.0,
            service_uuids=[WOSENW_SERVICE_UUID]
        )
        all_devices.extend(devices_with_services)
        
        unique_devices = {}
        for device in all_devices:
            if device.address not in unique_devices:
                unique_devices[device.address] = device
            else:
                # Keep the one with more information
                existing = unique_devices[device.address]
                if device.name and not existing.name:
                    unique_devices[device.address] = device
        
        devices = list(unique_devices.values())
        wosenw_devices = []
        
        for device in devices:
            device_data = self.get_device_info(device)
            
            # Focus specifically on WoSenW devices
            # NOTE: WoSenW is the name of the current model I have, to be tested
            # if this is always the name
            if device_data['name'] and device_data['name'] != 'Unknown':
                if "WoSenW" in device_data['name'] or "WoSen" in device_data['name']:
                    wosenw_devices.append({
                        'device': device,
                        'data': device_data,
                        'confidence': 5  # High confidence for WoSenW devices
                    })
        
        if not wosenw_devices:
            logger.warning("No WoSenW devices found")
        
        return [device_info['device'] for device_info in wosenw_devices]
    
    def is_similar_uuid(self, uuid):
        """Check if UUID has similar format to WoSenW UUIDs"""
        # Check if it's a valid UUID format
        if len(uuid) != 36:  # Standard UUID length
            return False
            
        # Check if it follows similar pattern (8-4-4-4-12 format)
        parts = uuid.split('-')
        if len(parts) != 5:
            return False
        
        # Check if it's a custom service UUID (not standard Bluetooth UUIDs)
        if uuid.startswith('0000') and uuid.endswith('-0000-1000-8000-00805f9b34fb'):
            return False  # Standard Bluetooth service
        
        # Check if it has similar structure to WoSenW UUIDs
        # WoSenW pattern: CBA20D00-224D-11E6-9FB8-0002A5D5C51B
        # Look for UUIDs that might be custom services
        if len(parts[0]) == 8 and len(parts[1]) == 4 and len(parts[2]) == 4:
            return True
        
        return False
    
    async def connect_to_device(self, device):
        """Connect to a WoSenW device"""
        self.client = BleakClient(device.address)
        await self.client.connect()
        return True
    
    async def discover_services(self):
        """Discover services and characteristics with flexible matching"""
        logger.info("🔍 Discovering services...")
        
        try:
            # Use the correct method to get services - try different approaches
            services = []
            
            # Try the most common method first
            try:
                services = await self.client.get_services()
            except AttributeError:
                try:
                    # Try alternative method
                    services = await self.client.discover_services()
                except AttributeError:
                    try:
                        # Try accessing services directly
                        services = self.client.services
                    except AttributeError:
                        # Last resort - try to get services from the device
                        logger.warning("⚠️ Could not discover services automatically, trying manual approach...")
                        # Try to connect and get services manually
                        await self.client.start_notify(WOSENW_NOTIFY_UUID, self.notification_handler)
                        services = []
            
            # Handle different types of service objects
            if hasattr(services, '__iter__'):
                # Convert to list if it's iterable
                services = list(services)
            elif hasattr(services, 'values'):
                # If it's a dict-like object
                services = list(services.values())
            elif hasattr(services, 'items'):
                # If it's a collection with items
                services = list(services.items())
            
            logger.info(f"Found {len(services)} services")
            
            # Store discovered characteristics for flexible access
            self.discovered_characteristics = {
                'notify': [],
                'write': [],
                'read': []
            }
            
            # Check for WoSenW service UUIDs
            wosenw_services_found = []
            similar_services_found = []
            
            # If we couldn't get services automatically, try to work with what we know
            if not services:
                logger.info("⚠️ No services discovered automatically, using known WoSenW characteristics...")
                
                # Add the known WoSenW characteristics
                from bleak.backends.characteristic import BleakGATTCharacteristic
                
                # Create mock characteristics for the known UUIDs
                notify_char = type('MockChar', (), {
                    'uuid': WOSENW_NOTIFY_UUID,
                    'properties': 0x10  # Notify
                })()
                
                write_char = type('MockChar', (), {
                    'uuid': WOSENW_WRITE_UUID,
                    'properties': 0x08  # Write
                })()
                
                self.discovered_characteristics['notify'].append(notify_char)
                self.discovered_characteristics['write'].append(write_char)
                
                logger.info(f"✅ Using known WoSenW characteristics:")
                logger.info(f"  Notify: {WOSENW_NOTIFY_UUID}")
                logger.info(f"  Write: {WOSENW_WRITE_UUID}")
                
                return True
            
            for service in services:
                logger.info(f"Service: {service.uuid}")
                
                # Check if this is a WoSenW service
                if service.uuid.lower() == WOSENW_SERVICE_UUID.lower():
                    wosenw_services_found.append(service.uuid)
                    logger.info(f"✅ Found exact WoSenW service: {service.uuid}")
                elif self.is_similar_uuid(service.uuid):
                    similar_services_found.append(service.uuid)
                    logger.info(f"⚠️ Found similar service: {service.uuid}")
                
                for char in service.characteristics:
                    logger.info(f"  Characteristic: {char.uuid} - Properties: {char.properties}")
                    
                    # Check if this is a WoSenW characteristic
                    if char.uuid.lower() in [WOSENW_NOTIFY_UUID.lower(), WOSENW_WRITE_UUID.lower()]:
                        logger.info(f"    ✅ WoSenW characteristic: {char.uuid}")
                    
                    # Categorize characteristics by properties - handle both string lists and integers
                    properties = char.properties
                    
                    # Convert string properties to integer if needed
                    if isinstance(properties, list):
                        # Properties is a list of strings like ['notify', 'write']
                        if 'notify' in properties or 'indicate' in properties:
                            self.discovered_characteristics['notify'].append(char)
                        if 'write' in properties or 'write-without-response' in properties:
                            self.discovered_characteristics['write'].append(char)
                        if 'read' in properties:
                            self.discovered_characteristics['read'].append(char)
                    else:
                        # Properties is an integer, use bitwise operations
                        if properties & 0x10:  # Notify
                            self.discovered_characteristics['notify'].append(char)
                        if properties & 0x08:  # Write
                            self.discovered_characteristics['write'].append(char)
                        if properties & 0x02:  # Read
                            self.discovered_characteristics['read'].append(char)
            
            logger.info(f"📊 Discovered characteristics:")
            logger.info(f"  Notify: {len(self.discovered_characteristics['notify'])}")
            logger.info(f"  Write: {len(self.discovered_characteristics['write'])}")
            logger.info(f"  Read: {len(self.discovered_characteristics['read'])}")
            
            if wosenw_services_found:
                logger.info(f"✅ Found {len(wosenw_services_found)} exact WoSenW services")
            if similar_services_found:
                logger.info(f"⚠️ Found {len(similar_services_found)} similar services")
            
            return True
        except Exception as e:
            logger.error(f"❌ Service discovery failed: {e}")
            return False
    
    def find_best_characteristics(self):
        """Find the best characteristics to use for communication"""
        notify_char = None
        write_char = None
        
        # Try exact UUIDs first
        for char in self.discovered_characteristics['notify']:
            if char.uuid.lower() == WOSENW_NOTIFY_UUID.lower():
                notify_char = char
                break
        
        for char in self.discovered_characteristics['write']:
            if char.uuid.lower() == WOSENW_WRITE_UUID.lower():
                write_char = char
                break
        
        # If exact matches not found, try similar ones
        if not notify_char and self.discovered_characteristics['notify']:
            notify_char = self.discovered_characteristics['notify'][0]
        
        if not write_char and self.discovered_characteristics['write']:
            write_char = self.discovered_characteristics['write'][0]
        
        # If still no characteristics found, create them from known UUIDs
        if not notify_char:
            notify_char = type('MockChar', (), {
                'uuid': WOSENW_NOTIFY_UUID,
                'properties': 0x10
            })()
        
        if not write_char:
            write_char = type('MockChar', (), {
                'uuid': WOSENW_WRITE_UUID,
                'properties': 0x08
            })()
        
        return notify_char, write_char
    
    async def initiate_handshake(self):
        """Initiate WoSenW-specific handshake sequence"""
        logger.info("🤝 Starting WoSenW handshake sequence...")
        
        # Find best characteristics to use
        notify_char, write_char = self.find_best_characteristics()
        
        if not write_char:
            logger.error("❌ No writable characteristic found")
            return False
        
        if not notify_char:
            logger.warning("⚠️ No notify characteristic found, handshake may not work properly")
        
        # Use only WoSenW handshake sequence
        sequence = HANDSHAKE_SEQUENCES["WoSenW"]
        self.current_step = 0
        self.handshake_completed = False
        self.received_responses = []
        
        # Subscribe to notifications first if available
        if notify_char:
            await self.subscribe_to_notifications(notify_char)
        
        logger.info(f"📋 WoSenW handshake sequence ({len(sequence)} steps):")
        for i, step in enumerate(sequence):
            logger.info(f"  Step {i+1}: {step.hex()}")
        
        for i, handshake_data in enumerate(sequence):
            self.current_step = i + 1
            logger.info(f"🤝 Handshake step {self.current_step}/{len(sequence)}: {handshake_data.hex()}")
            
            try:
                # Send handshake data using discovered characteristic
                await self.client.write_gatt_char(write_char.uuid, handshake_data)
                logger.info(f"📤 Sent handshake data to {write_char.uuid}")
                
                # Wait for response
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"❌ Failed to send handshake data: {e}")
                return False
        
        logger.info("✅ WoSenW handshake sequence completed")
        self.handshake_completed = True
        return True
    
    async def subscribe_to_notifications(self, notify_char=None):
        """Subscribe to device notifications with flexible characteristic selection"""
        if not notify_char:
            notify_char, _ = self.find_best_characteristics()
        
        await self.client.start_notify(notify_char.uuid, self.notification_handler)
        return True
    
    def notification_handler(self, sender, data):
        """Handle incoming notifications with enhanced WoSenW interpretation"""
        timestamp = asyncio.get_event_loop().time()
        
        logger.info(f"📥 [{timestamp:.1f}s] Received notification: {data.hex()}")
        self.received_responses.append(data)
        
        # Check if this is a handshake response
        if not self.handshake_completed and self.is_valid_handshake_response(data):
            logger.info("✅ Valid handshake response received")
        else:
            # Try to interpret WoSenW-specific notifications
            interpretation = self.interpret_wosenw_notification(data)
            if interpretation:
                logger.info(f"📡 WoSenW Event: {interpretation}")
            else:
                logger.info("📡 Regular device data received")
    
    def interpret_wosenw_notification(self, data):
        """Interpret WoSenW-specific notifications"""
        if len(data) < 2:
            return None
        
        try:
            # Common WoSenW notification patterns
            if len(data) == 2:
                first_byte = data[0]
                second_byte = data[1]
                
                # Status responses
                if first_byte == 0x53:  # 'S' for Status
                    return "Status response received"
                elif first_byte == 0x4D:  # 'M' for Monitor
                    return "Monitoring response received"
                elif first_byte == 0x49:  # 'I' for Info
                    return "Device info response received"
                elif first_byte == 0x50:  # 'P' for Ping
                    return "Ping response received"
                elif first_byte == 0x4C:  # 'L' for Leak
                    return "Leak status response received"
                elif first_byte == 0x42:  # 'B' for Battery
                    return "Battery status response received"
                elif first_byte == 0x54:  # 'T' for Temperature
                    return "Temperature response received"
                elif first_byte == 0x48:  # 'H' for Humidity
                    return "Humidity response received"
            
            # Try to decode as string
            try:
                string_data = data.decode('utf-8')
                if string_data:
                    return f"String data: {string_data}"
            except:
                pass
            
            # Check for specific WoSenW event patterns
            if len(data) >= 4:
                # Leak detection event
                if data[0:2] == b'\x4C\x45':  # "LE" for Leak
                    return "Leak detection event"
                # Battery low event
                elif data[0:2] == b'\x42\x41':  # "BA" for Battery
                    return "Battery status event"
                # Temperature event
                elif data[0:2] == b'\x54\x45':  # "TE" for Temperature
                    return "Temperature event"
                # Humidity event
                elif data[0:2] == b'\x48\x55':  # "HU" for Humidity
                    return "Humidity event"
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error interpreting notification: {e}")
            return None
    
    def is_valid_handshake_response(self, data):
        """Check if data is a valid handshake response"""
        if len(data) < 2:
            return False
        
        first_byte = data[0]
        second_byte = data[1]
        
        # WoSenW response patterns
        responses = [
            (0x01, 0x01),  # Acknowledge
            (0x02, 0x00),  # Confirm
            (0x03, 0x01),  # Info response
            (0x04, 0x00),  # Notification enabled
            (0x05, 0x01),  # Handshake complete
        ]
        
        return (first_byte, second_byte) in responses
    
    async def send_wosenw_commands(self):
        """Send WoSenW-specific test commands"""
        logger.info("🧪 Sending WoSenW-specific test commands...")
        
        # Find best characteristics to use
        notify_char, write_char = self.find_best_characteristics()
        
        if not write_char:
            logger.error("❌ No writable characteristic found for WoSenW commands")
            return
        
        # WoSenW-specific commands
        wosenw_commands = [
            (b"STAT", "Request device status"),
            (b"MONI", "Start event monitoring"),
            (b"INFO", "Request device information"),
            (b"PING", "Send ping command"),
            (b"TEST", "Test command"),
            (b"HELP", "Request help/commands"),
            # (b"LEAK", "Check leak status"),
            (b"BATT", "Check battery status"),
        ]
        
        # WoSenW handshake-like commands
        wosenw_handshake_commands = [
            (b"\x01\x00", "WoSenW handshake 1"),
            (b"\x02\x01", "WoSenW handshake 2"),
            (b"\x03\x00", "WoSenW handshake 3"),
            (b"\x04\x01", "WoSenW handshake 4"),
            (b"\x05\x00", "WoSenW handshake 5"),
        ]
        
        all_commands = wosenw_commands + wosenw_handshake_commands
        
        for command, description in all_commands:
            try:
                logger.info(f"📤 Sending WoSenW {description}: {command.hex()}")
                await self.client.write_gatt_char(write_char.uuid, command)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ Failed to send WoSenW {description}: {e}")
    
    async def send_test_commands(self):
        """Send test commands to the device with flexible characteristic selection"""
        # This method now calls the WoSenW-specific version
        await self.send_wosenw_commands()
    
    async def try_read_characteristics(self):
        """Try to read from all readable characteristics"""
        logger.info("📖 Trying to read from readable characteristics...")
        
        for char in self.discovered_characteristics['read']:
            try:
                logger.info(f"📖 Reading from {char.uuid}...")
                value = await self.client.read_gatt_char(char.uuid)
                logger.info(f"📥 Read value from {char.uuid}: {value.hex()}")
                
                # Try to interpret as string
                try:
                    string_value = value.decode('utf-8')
                    logger.info(f"📝 String value: {string_value}")
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"❌ Failed to read from {char.uuid}: {e}")
    
    async def run_full_test(self):
        """Run complete WoSenW-specific handshake test"""
        logger.info("🚀 Starting WoSenW-specific handshake test...")
        
        try:
            # Scan for WoSenW devices specifically
            devices = await self.scan_for_devices()
            
            # Connect to the first WoSenW device found
            device = devices[0]
            await self.connect_to_device(device)
            
            # Discover services
            await self.discover_services()
            
            # Try to read from characteristics first
            await self.try_read_characteristics()
            
            # Perform WoSenW handshake
            await self.initiate_handshake()
            
            # Send WoSenW-specific test commands
            await self.send_wosenw_commands()
            
            # Wait for any additional responses
            await asyncio.sleep(5.0)
            
            # Check battery status specifically
            # await self.check_battery_status()
            
            # for _, response in enumerate(self.received_responses):
            #     response.decode('utf-8')
            
            # await self.monitor_notifications()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False
    
    async def monitor_notifications(self):
        """Keep connection open and monitor for notifications"""
        while True:
            await asyncio.sleep(1.0)
            if not self.client.is_connected:
                break

    def get_device_info(self, device):
        """Safely get device information regardless of bleak version"""
        info = {
            'name': device.name or 'Unknown',
            'address': device.address,
            'rssi': None,
            'manufacturer_data': None,
            'service_uuids': []
        }
        
        # Try different ways to get RSSI
        if hasattr(device, 'rssi') and device.rssi:
            info['rssi'] = device.rssi
        elif hasattr(device, 'advertisement') and hasattr(device.advertisement, 'rssi'):
            info['rssi'] = device.advertisement.rssi
        
        # Try different ways to get manufacturer data
        if hasattr(device, 'metadata') and device.metadata:
            if 'manufacturer_data' in device.metadata:
                info['manufacturer_data'] = device.metadata['manufacturer_data']
            if 'service_uuids' in device.metadata:
                info['service_uuids'] = device.metadata['service_uuids']
        
        # Try advertisement data
        if hasattr(device, 'advertisement'):
            if hasattr(device.advertisement, 'manufacturer_data'):
                info['manufacturer_data'] = device.advertisement.manufacturer_data
            if hasattr(device.advertisement, 'service_uuids'):
                info['service_uuids'] = device.advertisement.service_uuids
        
        return info
    
    async def ping_sensor(self, command: bytes = b"\x57\x02"):
        """Ping the sensor to get the current status"""
        logger.info("Pinging sensor...")
        
        _, write_char = self.find_best_characteristics()
        
        self.received_responses = []

        # 0x57 is the command to ping the sensor
        await self.client.write_gatt_char(write_char.uuid, command)
        await asyncio.sleep(2.0)
        
        if self.received_responses:
            response = self.received_responses[-1]
            return response.hex()
        return None

async def main():
    """Main test function"""
    tester = WoSenWHandshakeTester()
    success = await tester.run_full_test()

    if success:
        logger.info("✅ Handshake test completed successfully")
    else:
        logger.error("❌ Handshake test failed")

    # Commands to test
    commands = [
        b"\x57\x00\x02",
        b"\x57\x00\x11",
        b"\x57\x00\x12",
    ]

    for command in commands :
        status = await tester.ping_sensor(command)
        print(f"Status: {status}")
        await asyncio.sleep(3.0)
        print(f"Decoded: {decode_wosenw_status_packet(status)}")
    

if __name__ == "__main__":
    asyncio.run(main()) 