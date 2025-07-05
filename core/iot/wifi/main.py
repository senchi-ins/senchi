"""
Persistent SwitchBot Leak Detector Connection & Pairing
Creates a sustained connection and attempts to pair the device with macOS
"""

import asyncio
import logging
from bleak import BleakClient, BleakScanner
import time
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your detected device
LEAK_DETECTOR_MAC = "ECD25189-92D0-6712-8C02-86B4D17BA636"

# Extended connection timeout for pairing
CONNECTION_TIMEOUT = 30.0
MONITORING_DURATION = 60.0  # Monitor for 1 minute

# FFF6: 0x0011089713E90701

class SwitchBotLeakDetector:
    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.client = None
        self.is_connected = False
        self.device_data = {
            'mac_address': mac_address,
            'connection_info': {},
            'services': {},
            'characteristics': {},
            'notifications': {},
            'pairing_status': 'unknown',
            'raw_data_captured': []
        }
    
    async def connect_and_pair(self):
        """Connect to device and attempt pairing"""
        print(f"🔗 Attempting persistent connection to {self.mac_address}...")
        
        try:
            # Create client with extended timeout
            self.client = BleakClient(
                self.mac_address, 
                timeout=CONNECTION_TIMEOUT,
                disconnected_callback=self.disconnected_callback
            )
            
            # Connect
            await self.client.connect()
            self.is_connected = True
            
            print(f"✅ Connected successfully!")
            print(f"🔗 Connection MTU: {self.client.mtu_size}")
            
            # Try to get device info from the connection
            self.device_data['connection_info'] = {
                'mtu_size': self.client.mtu_size,
                'is_connected': self.client.is_connected,
                'address': str(self.client.address)
            }
            
            # Note: Core Bluetooth doesn't support programmatic pairing
            print(f"📝 Note: Programmatic pairing not available in Core Bluetooth")
            print(f"💡 For persistent pairing: Use System Preferences > Bluetooth manually")
            self.device_data['pairing_status'] = 'core_bluetooth_limitation'
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.device_data['pairing_status'] = f'connection_failed: {str(e)}'
            return False
    
    def disconnected_callback(self, client):
        """Called when device disconnects"""
        print(f"🔌 Device disconnected: {client.address}")
        self.is_connected = False
    
    async def discover_all_services(self):
        """Comprehensive service and characteristic discovery"""
        if not self.is_connected:
            return False
        
        print(f"\n🔍 Discovering all services and characteristics...")
        
        try:
            services = self.client.services
            
            for service in services:
                service_uuid = str(service.uuid)
                service_info = {
                    'uuid': service_uuid,
                    'description': service.description,
                    'characteristics': {}
                }
                
                print(f"\n📡 Service: {service_uuid}")
                if service.description:
                    print(f"   Description: {service.description}")
                
                for char in service.characteristics:
                    char_uuid = str(char.uuid)
                    char_info = {
                        'uuid': char_uuid,
                        'description': char.description,
                        'properties': list(char.properties),
                        'descriptors': [],
                        'data': None,
                        'data_interpretation': None
                    }
                    
                    print(f"   📝 Characteristic: {char_uuid}")
                    print(f"      Properties: {char.properties}")
                    
                    # Get descriptors
                    for descriptor in char.descriptors:
                        desc_info = {
                            'uuid': str(descriptor.uuid),
                            'description': descriptor.description
                        }
                        char_info['descriptors'].append(desc_info)
                        print(f"      🏷️  Descriptor: {descriptor.uuid}")
                    
                    # Try to read if possible
                    if "read" in char.properties:
                        try:
                            data = await self.client.read_gatt_char(char.uuid)
                            char_info['data'] = data.hex()
                            char_info['data_interpretation'] = self.interpret_data(data, char_uuid)
                            print(f"      📄 Data: {data.hex()}")
                            print(f"      🔍 Interpretation: {char_info['data_interpretation']}")
                        except Exception as e:
                            char_info['data'] = f"read_error: {str(e)}"
                            print(f"      ❌ Read error: {e}")
                    
                    # Set up notification if possible
                    if "notify" in char.properties:
                        try:
                            await self.client.start_notify(char.uuid, self.create_notification_handler(char_uuid))
                            char_info['notification_active'] = True
                            print(f"      🔔 Notification enabled")
                        except Exception as e:
                            char_info['notification_active'] = False
                            print(f"      ❌ Notification failed: {e}")
                    
                    service_info['characteristics'][char_uuid] = char_info
                
                self.device_data['services'][service_uuid] = service_info
            
            return True
            
        except Exception as e:
            print(f"❌ Service discovery failed: {e}")
            return False
    
    def create_notification_handler(self, char_uuid):
        """Create a notification handler for a specific characteristic"""
        def handler(sender, data):
            timestamp = time.strftime("%H:%M:%S")
            interpretation = self.interpret_data(data, char_uuid)
            
            notification_info = {
                'timestamp': timestamp,
                'characteristic': char_uuid,
                'data': data.hex(),
                'interpretation': interpretation
            }
            
            self.device_data['raw_data_captured'].append(notification_info)
            print(f"🔔 [{timestamp}] {char_uuid}: {data.hex()} - {interpretation}")
        
        return handler
    
    def interpret_data(self, data, char_uuid):
        """Enhanced data interpretation"""
        if len(data) == 0:
            return "Empty data"
        
        interpretations = []
        
        # Standard GATT characteristics
        if "2a19" in char_uuid.lower():  # Battery Level
            if len(data) >= 1:
                battery = data[0]
                interpretations.append(f"Battery: {battery}%")
        
        elif "2a29" in char_uuid.lower():  # Manufacturer Name
            try:
                manufacturer = data.decode('utf-8').strip('\x00')
                interpretations.append(f"Manufacturer: {manufacturer}")
            except:
                interpretations.append(f"Manufacturer (hex): {data.hex()}")
        
        elif "2a24" in char_uuid.lower():  # Model Number
            try:
                model = data.decode('utf-8').strip('\x00')
                interpretations.append(f"Model: {model}")
            except:
                interpretations.append(f"Model (hex): {data.hex()}")
        
        elif "2a26" in char_uuid.lower():  # Firmware Revision
            try:
                firmware = data.decode('utf-8').strip('\x00')
                interpretations.append(f"Firmware: {firmware}")
            except:
                interpretations.append(f"Firmware (hex): {data.hex()}")
        
        # SwitchBot specific patterns
        elif "fd3d" in char_uuid.lower():  # SwitchBot service
            if len(data) >= 1:
                # Common SwitchBot data patterns
                first_byte = data[0]
                if first_byte == 0x57:  # 'W' - common SwitchBot prefix
                    interpretations.append("SwitchBot sensor data")
                    if len(data) >= 4:
                        # Try to extract sensor values
                        temp = int.from_bytes(data[2:4], byteorder='little', signed=True) / 10.0
                        interpretations.append(f"Possible temp: {temp}°C")
                elif first_byte in [0x00, 0x01]:
                    status = "No leak" if first_byte == 0x00 else "LEAK DETECTED"
                    interpretations.append(f"Leak status: {status}")
        
        # Generic interpretation
        if not interpretations:
            if len(data) == 1:
                interpretations.append(f"Single byte: {data[0]} (0x{data[0]:02x})")
            elif len(data) == 2:
                value = int.from_bytes(data, byteorder='little')
                interpretations.append(f"16-bit value: {value}")
            else:
                interpretations.append(f"Data ({len(data)} bytes): {data.hex()}")
        
        return " | ".join(interpretations)
    
    async def monitor_device(self, duration=60):
        """Monitor device for ongoing data"""
        print(f"\n📊 Monitoring device for {duration} seconds...")
        print(f"Keep the device active (try triggering water detection with a wet finger)")
        
        start_time = time.time()
        while time.time() - start_time < duration and self.is_connected:
            await asyncio.sleep(1)
            
            # Periodically check connection
            if not self.client.is_connected:
                print(f"🔌 Connection lost during monitoring")
                break
        
        print(f"📊 Monitoring complete")
    
    async def disconnect(self):
        """Clean disconnect"""
        if self.client and self.is_connected:
            try:
                await self.client.disconnect()
                print(f"🔌 Disconnected from device")
            except:
                pass
        self.is_connected = False
    
    def save_device_profile(self, filename="leak_detector_profile.json"):
        """Save comprehensive device profile"""
        with open(filename, 'w') as f:
            json.dump(self.device_data, f, indent=2)
        print(f"💾 Device profile saved to {filename}")

async def main():
    """Main execution with persistent connection"""
    print("SwitchBot Leak Detector - Persistent Connection & Pairing")
    print("=========================================================")
    print(f"Target: {LEAK_DETECTOR_MAC}")
    print(f"Goal: Create sustained connection for iOS app development\n")
    
    detector = SwitchBotLeakDetector(LEAK_DETECTOR_MAC)
    
    try:
        # Step 1: Connect and pair
        if await detector.connect_and_pair():
            
            # Step 2: Discover everything
            await detector.discover_all_services()
            
            # Step 3: Monitor for data
            await detector.monitor_device(MONITORING_DURATION)
            
            # Step 4: Save profile
            detector.save_device_profile()
            
            print(f"\n🎯 CONNECTION SUMMARY")
            print(f"=" * 50)
            print(f"✅ Connection: Successful")
            print(f"🤝 Pairing: {detector.device_data['pairing_status']}")
            print(f"📡 Services discovered: {len(detector.device_data['services'])}")
            print(f"🔔 Notifications captured: {len(detector.device_data['raw_data_captured'])}")
            
            print(f"\n📱 FOR iOS APP DEVELOPMENT:")
            print(f"   MAC Address: {LEAK_DETECTOR_MAC}")
            print(f"   Services: {list(detector.device_data['services'].keys())}")
            print(f"   Device profile saved with all characteristics")
            
            print(f"\n🔗 FOR PERSISTENT PAIRING:")
            print(f"   1. Go to System Preferences > Bluetooth")
            print(f"   2. Put SwitchBot in pairing mode")
            print(f"   3. Click 'Connect' when it appears")
            print(f"   4. Once paired, your iOS app can connect without re-pairing")
            
            print(f"\n💡 iOS APP CONNECTION TIPS:")
            print(f"   - Use CBCentralManager to scan for this device")
            print(f"   - Connect using the MAC address: {LEAK_DETECTOR_MAC}")
            print(f"   - Main service UUID: 0000fd3d-0000-1000-8000-00805f9b34fb")
            print(f"   - Check saved profile for all available characteristics")
        
        else:
            print(f"❌ Failed to establish connection")
    
    finally:
        await detector.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()