import asyncio
import logging

logger = logging.getLogger(__name__)

def decode_wosenw_status_packet(data_hex):
    """Decode WoSenW status packet from SwitchBot protocol"""
    
    # Convert hex string to bytes
    if isinstance(data_hex, str):
        data = bytes.fromhex(data_hex)
    else:
        data = data_hex
    
    print(f"📊 Decoding WoSenW status packet: {data.hex()}")
    print(f"📏 Packet length: {len(data)} bytes")
    print(f"🔢 Raw bytes: {[f'0x{b:02x}' for b in data]}")
    print(f"🔢 Decimal values: {[b for b in data]}")
    print()
    
    if len(data) >= 12:
        # Decode each byte based on SwitchBot sensor protocol
        status_byte = data[0]      # 0x01 = Status response
        battery_level = data[1]    # 0x64 = 100 (decimal) = 100% battery
        sensor_type = data[2]      # 0x0E = Sensor type identifier
        sensor_status = data[3]    # 0x3F = Sensor status flags
        
        # Bytes 4-9 appear to be reserved/padding (all 0x00)
        reserved = data[4:10]
        
        # Bytes 10-11 might be additional status or checksum
        additional_status = data[10]  # 0x0E
        checksum_or_end = data[11]    # 0x00
        
        print("🔍 DECODED PACKET STRUCTURE:")
        print(f"  Byte 0 (Status):     0x{status_byte:02x} = {status_byte}")
        print(f"  Byte 1 (Battery):    0x{battery_level:02x} = {battery_level}% 🔋")
        print(f"  Byte 2 (Sensor Type): 0x{sensor_type:02x} = {sensor_type}")
        print(f"  Byte 3 (Sensor Status): 0x{sensor_status:02x} = {sensor_status:08b}b")
        print(f"  Bytes 4-9 (Reserved): {[f'0x{b:02x}' for b in reserved]}")
        print(f"  Byte 10 (Additional): 0x{additional_status:02x} = {additional_status}")
        print(f"  Byte 11 (End/Check): 0x{checksum_or_end:02x} = {checksum_or_end}")
        print()
        
        # Decode sensor status flags (byte 3)
        print("🚨 SENSOR STATUS FLAGS (Byte 3):")
        status_flags = sensor_status
        
        leak_detected = bool(status_flags & 0x01)      # Bit 0
        low_battery = bool(status_flags & 0x02)        # Bit 1  
        sensor_error = bool(status_flags & 0x04)       # Bit 2
        tamper_alert = bool(status_flags & 0x08)       # Bit 3
        test_mode = bool(status_flags & 0x10)          # Bit 4
        monitoring_active = bool(status_flags & 0x20)  # Bit 5
        
        print(f"  🚰 Leak Detected:     {'YES' if leak_detected else 'NO'}")
        print(f"  🪫 Low Battery:       {'YES' if low_battery else 'NO'}")
        print(f"  ❌ Sensor Error:      {'YES' if sensor_error else 'NO'}")
        print(f"  🚨 Tamper Alert:      {'YES' if tamper_alert else 'NO'}")
        print(f"  🧪 Test Mode:         {'YES' if test_mode else 'NO'}")
        print(f"  📡 Monitoring:        {'ACTIVE' if monitoring_active else 'INACTIVE'}")
        print()
        
        # Summary
        print("📋 DEVICE SUMMARY:")
        print(f"  🔋 Battery Level: {battery_level}%")
        print(f"  💧 Leak Status: {'DETECTED' if leak_detected else 'CLEAR'}")
        print(f"  🔧 Device Health: {'ERROR' if sensor_error else 'OK'}")
        print(f"  📡 Monitoring: {'ON' if monitoring_active else 'OFF'}")
        
        return {
            'battery_level': battery_level,
            'leak_detected': leak_detected,
            'low_battery': low_battery,
            'sensor_error': sensor_error,
            'tamper_alert': tamper_alert,
            'test_mode': test_mode,
            'monitoring_active': monitoring_active,
            'sensor_type': sensor_type,
            'raw_data': data.hex()
        }
    else:
        print("❌ Packet too short for full decode")
        return None

# Enhanced notification handler for your class
def enhanced_notification_handler_with_decoder(self, sender, data):
    """Enhanced notification handler with packet decoding"""
    timestamp = asyncio.get_event_loop().time()
    
    print(f"📥 [{timestamp:.1f}s] Received notification: {data.hex()}")
    self.received_responses.append(data)
    
    # Check if this is a status packet (starts with 0x01 and is long enough)
    if len(data) >= 12 and data[0] == 0x01:
        print("🎯 DETECTED STATUS PACKET! Decoding...")
        decoded = decode_wosenw_status_packet(data)
        
        if decoded:
            print(f"✅ Battery: {decoded['battery_level']}%")
            print(f"💧 Leak: {'DETECTED' if decoded['leak_detected'] else 'CLEAR'}")
            print(f"📡 Monitoring: {'ON' if decoded['monitoring_active'] else 'OFF'}")
            
            # Store decoded data
            self.last_status = decoded
            
    elif len(data) == 1:
        # Single byte status codes
        byte_val = data[0]
        status_codes = {
            0x01: "✅ ACK",
            0x05: "🔄 READY", 
        }
        print(f"📡 Status: {status_codes.get(byte_val, f'Unknown: 0x{byte_val:02x}')}")
    else:
        print(f"📊 Other data: {data.hex()}")

# Working command functions
async def get_device_status(self):
    """Get complete device status using working SwitchBot command"""
    logger.info("📊 Getting device status...")
    
    notify_char, write_char = self.find_best_characteristics()
    
    if not write_char:
        logger.error("❌ No write characteristic found")
        return None
    
    try:
        # Clear previous responses
        self.received_responses = []
        
        # Send the working SwitchBot status command
        status_command = b"\x57\x02"  # This worked!
        logger.info(f"📤 Sending status command: {status_command.hex()}")
        
        await self.client.write_gatt_char(write_char.uuid, status_command)
        
        # Wait for response
        await asyncio.sleep(2.0)
        
        if self.received_responses:
            response = self.received_responses[-1]
            logger.info(f"📥 Status response: {response.hex()}")
            
            # Decode if it's a status packet
            if len(response) >= 12 and response[0] == 0x01:
                decoded = decode_wosenw_status_packet(response)
                return decoded
            else:
                logger.warning(f"⚠️ Unexpected response format: {response.hex()}")
                return None
        else:
            logger.error("❌ No response to status command")
            return None
            
    except Exception as e:
        logger.error(f"❌ Status command failed: {e}")
        return None

async def monitor_with_periodic_status(self):
    """Monitor with periodic status updates"""
    logger.info("👁️ Starting monitoring with periodic status updates...")
    logger.info("💡 Try triggering the leak sensor now!")
    
    try:
        last_status_time = 0
        status_interval = 10  # Get status every 10 seconds
        
        while True:
            current_time = asyncio.get_event_loop().time()
            
            # Get periodic status updates
            if current_time - last_status_time > status_interval:
                logger.info("🔄 Getting periodic status update...")
                status = await self.get_device_status()
                
                if status:
                    logger.info(f"📊 Current Status:")
                    logger.info(f"  🔋 Battery: {status['battery_level']}%")
                    logger.info(f"  💧 Leak: {'DETECTED' if status['leak_detected'] else 'CLEAR'}")
                    logger.info(f"  📡 Monitoring: {'ON' if status['monitoring_active'] else 'OFF'}")
                    
                    # Alert on status changes
                    if hasattr(self, 'previous_status'):
                        if status['leak_detected'] != self.previous_status.get('leak_detected'):
                            if status['leak_detected']:
                                logger.info("🚨 LEAK DETECTION EVENT!")
                            else:
                                logger.info("✅ LEAK CLEARED!")
                                
                        if abs(status['battery_level'] - self.previous_status.get('battery_level', 0)) > 5:
                            logger.info(f"🔋 Battery level changed: {status['battery_level']}%")
                    
                    self.previous_status = status
                
                last_status_time = current_time
            
            await asyncio.sleep(1.0)
            
            # Check for spontaneous notifications
            if self.received_responses:
                for response in self.received_responses:
                    if len(response) >= 12 and response[0] == 0x01:
                        logger.info("📥 Spontaneous status update received!")
                        decode_wosenw_status_packet(response)
                self.received_responses = []
            
    except KeyboardInterrupt:
        logger.info("🛑 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitoring error: {e}")

# Test the decoder with your actual data
print("🧪 Testing decoder with your actual response...")
# decode_wosenw_status_packet("01640e3f0000000000000e00")
decode_wosenw_status_packet("0f64886866cba93c010000000071")

# While holding the button, the sensor sends this:
# 0f64886866cba93c016866d06d72

# 01640e3f0000000000000e00

# 01640e3f0000000000000e00