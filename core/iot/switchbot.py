#!/usr/bin/env python3
"""
SwitchBot Command Test - Try to get data without triggering water mode
"""

import asyncio
import logging
from bleak import BleakClient
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LEAK_DETECTOR_MAC = "ECD25189-92D0-6712-8C02-86B4D17BA636"
SERVICE_UUID = "cba20d00-224d-11e6-9fb8-0002a5d5c51b"
WRITE_CHAR = "cba20002-224d-11e6-9fb8-0002a5d5c51b"
NOTIFY_CHAR = "cba20003-224d-11e6-9fb8-0002a5d5c51b"

# Common SwitchBot commands to try
TEST_COMMANDS = [
    bytes([0x57, 0x01]),  # Common SwitchBot status request
    bytes([0x57, 0x02]),  # Another status command
    bytes([0x01]),        # Simple ping
    bytes([0x00]),        # Status query
    bytes([0x57, 0x0F, 0x51, 0x01]),  # SwitchBot standard query
]

class SwitchBotTester:
    def __init__(self):
        self.notifications_received = []
        self.connected = False
    
    async def notification_handler(self, sender, data):
        """Handle incoming notifications"""
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"🔔 [{timestamp}] Notification: {data.hex()} ({len(data)} bytes)")
        
        # Try to interpret the data
        interpretation = self.interpret_notification(data)
        print(f"   Interpretation: {interpretation}")
        
        self.notifications_received.append({
            'timestamp': timestamp,
            'data': data.hex(),
            'interpretation': interpretation
        })
    
    def interpret_notification(self, data):
        """Try to interpret notification data"""
        if len(data) == 0:
            return "Empty notification"
        
        interpretations = []
        
        # Check for SwitchBot response patterns
        if data[0] == 0x57:  # 'W' - SwitchBot response prefix
            interpretations.append("SwitchBot response")
            if len(data) >= 2:
                cmd = data[1]
                if cmd == 0x01:
                    interpretations.append("Status response")
                elif cmd == 0x02:
                    interpretations.append("Sensor data response")
        
        # Check for leak status
        elif data[0] == 0x00:
            interpretations.append("No leak detected")
        elif data[0] == 0x01:
            interpretations.append("LEAK DETECTED!")
        
        # Check for battery info
        if len(data) >= 2 and 0 <= data[1] <= 100:
            interpretations.append(f"Possible battery: {data[1]}%")
        
        # Raw interpretation
        interpretations.append(f"Raw: {' '.join(f'{b:02x}' for b in data)}")
        
        return " | ".join(interpretations)
    
    async def test_commands(self):
        """Test various commands to get device data"""
        print(f"🔗 Connecting to {LEAK_DETECTOR_MAC}...")
        
        try:
            async with BleakClient(LEAK_DETECTOR_MAC, timeout=15.0) as client:
                self.connected = True
                print(f"✅ Connected!")
                
                # Set up notifications
                await client.start_notify(NOTIFY_CHAR, self.notification_handler)
                print(f"🔔 Notifications enabled")
                
                # Wait a moment for any immediate notifications
                print(f"⏳ Waiting for initial notifications...")
                await asyncio.sleep(3)
                
                # Try sending various commands
                print(f"\n🧪 Testing commands...")
                for i, command in enumerate(TEST_COMMANDS, 1):
                    print(f"\n--- Command {i}: {command.hex()} ---")
                    try:
                        await client.write_gatt_char(WRITE_CHAR, command, response=False)
                        print(f"✅ Command sent")
                        
                        # Wait for response
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        print(f"❌ Command failed: {e}")
                
                # Monitor for additional data
                print(f"\n📊 Monitoring for 20 seconds...")
                print(f"Try gently tapping the device or moving it around")
                await asyncio.sleep(20)
                
                print(f"\n📈 Test complete!")
                print(f"Total notifications received: {len(self.notifications_received)}")
                
                return self.notifications_received
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return []

async def main():
    """Main test function"""
    print("SwitchBot Leak Detector Command Test")
    print("===================================")
    print("Testing commands without triggering water detection\n")
    
    tester = SwitchBotTester()
    results = await tester.test_commands()
    
    if results:
        print(f"\n🎯 RESULTS SUMMARY:")
        print(f"=" * 40)
        for i, notification in enumerate(results, 1):
            print(f"{i}. [{notification['timestamp']}] {notification['interpretation']}")
        
        # Save results
        import json
        with open('switchbot_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to switchbot_test_results.json")
    else:
        print(f"\n❌ No data captured")
        print(f"This device might only respond to actual water detection")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")