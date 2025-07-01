#!/bin/bash

# BLE Advertisement Scanner for SwitchBot devices on macOS
# This script focuses specifically on BLE advertisements

echo "BLE Advertisement Scanner for SwitchBot (macOS)"
echo "==============================================="
echo

# Check dependencies
if ! command -v blueutil &> /dev/null; then
    echo "Error: blueutil not found. Install with: brew install blueutil"
    exit 1
fi

echo "Step 1: Enabling Bluetooth and verbose logging..."
echo "------------------------------------------------"

# Ensure Bluetooth is on
blueutil -p 1
sleep 2

echo "✓ Bluetooth enabled"
echo

echo "Step 2: Scanning for BLE advertisements..."
echo "-----------------------------------------"
echo "This will monitor BLE advertisements specifically."
echo "Keep your SwitchBot sensor close and in pairing mode!"
echo

# Create a temporary script to monitor Bluetooth logs
LOG_MONITOR_SCRIPT="/tmp/ble_monitor.sh"
cat > "$LOG_MONITOR_SCRIPT" << 'EOF'
#!/bin/bash
# Monitor system logs for BLE advertisements
log stream --predicate 'subsystem == "com.apple.bluetooth"' --level debug 2>/dev/null | while read line; do
    if [[ "$line" == *"advertisement"* ]] || [[ "$line" == *"peripheral"* ]] || [[ "$line" == *"RSSI"* ]]; then
        echo "$(date '+%H:%M:%S') - $line"
    fi
done
EOF

chmod +x "$LOG_MONITOR_SCRIPT"

echo "Starting BLE advertisement monitoring (30 seconds)..."
echo "Look for devices with names like 'WoSensorTH' or MAC addresses..."
echo

# Start log monitoring in background
"$LOG_MONITOR_SCRIPT" &
LOG_PID=$!

# Also try to scan using system_profiler repeatedly
for i in {1..6}; do
    echo "Scan attempt $i/6..."
    
    # Reset and scan
    blueutil --inquiry 5 2>/dev/null | grep -i -E "(switch|bot|sensor|wo)" &
    
    # Check system profiler
    system_profiler SPBluetoothDataType 2>/dev/null | grep -A 10 -B 5 -i -E "(switch|bot|sensor|wo|device)" | grep -v "^$" &
    
    sleep 5
done

# Stop log monitoring
kill $LOG_PID 2>/dev/null

echo
echo "Step 3: Checking for low-level BLE devices..."
echo "--------------------------------------------"

# Try to get more detailed BLE information
echo "Checking for BLE peripherals in system..."
system_profiler SPBluetoothDataType 2>/dev/null | grep -A 20 -B 5 -i "low energy"

echo
echo "Step 4: Alternative detection methods..."
echo "---------------------------------------"

# Check if device appears in recent connections
echo "Recent Bluetooth activity:"
blueutil --recent 20 2>/dev/null

echo
echo "Step 5: Manual MAC address patterns..."
echo "-------------------------------------"
echo "SwitchBot devices often use MAC addresses starting with:"
echo "- 60:55:F9:xx:xx:xx"
echo "- 54:2E:30:xx:xx:xx" 
echo "- Other common IoT prefixes"
echo

# Try to find any devices with these patterns
ALL_DEVICES=$(system_profiler SPBluetoothDataType 2>/dev/null)
echo "Checking for common SwitchBot MAC prefixes..."

if echo "$ALL_DEVICES" | grep -i "60:55:F9\|54:2E:30" > /dev/null; then
    echo "✓ Found device with SwitchBot MAC prefix:"
    echo "$ALL_DEVICES" | grep -i -A 5 -B 5 "60:55:F9\|54:2E:30"
else
    echo "No devices found with common SwitchBot MAC prefixes"
fi

echo
echo "Step 6: Advanced debugging..."
echo "-----------------------------"

# Check if Core Bluetooth is working
echo "Testing Core Bluetooth functionality..."
python3 -c "
import subprocess
import sys
try:
    # Try to import CoreBluetooth via PyObjC if available
    from Foundation import *
    print('✓ Foundation framework accessible')
except ImportError:
    print('⚠ PyObjC not available for advanced Core Bluetooth access')

# Alternative: check if we can see BLE advertisements via system logs
print('Checking system Bluetooth logs...')
" 2>/dev/null

echo
echo "Step 7: Diagnostic information..."
echo "--------------------------------"
echo "Current Bluetooth status:"
blueutil -p
echo

echo "Bluetooth controller info:"
system_profiler SPBluetoothDataType | head -20

echo
echo "Step 8: Troubleshooting recommendations..."
echo "-----------------------------------------"
echo "If the device still isn't detected:"
echo
echo "1. **Try a different approach:**"
echo "   - Download 'Bluetooth Explorer' from Apple Developer Tools"
echo "   - Use 'LightBlue Explorer' from the App Store"
echo "   - These tools are better at detecting BLE advertisements"
echo
echo "2. **Check SwitchBot specific behavior:**"
echo "   - Some SwitchBot devices only advertise when NOT in the app"
echo "   - Try completely removing from SwitchBot app first"
echo "   - The device might need to be 'unclaimed' entirely"
echo
echo "3. **macOS permissions:**"
echo "   - Check System Preferences > Security & Privacy > Privacy > Bluetooth"
echo "   - Make sure relevant apps have Bluetooth access"
echo
echo "4. **Hardware troubleshooting:**"
echo "   - Try with the sensor very close (< 1 meter) to your Mac"
echo "   - Check if other BLE devices work with your Mac"
echo "   - Reset Mac's Bluetooth: sudo pkill bluetoothd"
echo
echo "5. **Alternative integration path:**"
echo "   - Consider using an ESP32 as a BLE-to-MQTT bridge"
echo "   - This bypasses macOS BLE limitations entirely"

# Cleanup
rm -f "$LOG_MONITOR_SCRIPT" 2>/dev/null

echo
echo "Scan complete!"
echo "If no SwitchBot device was found, try the troubleshooting steps above."