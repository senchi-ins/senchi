# SwitchBot Leak Detector iOS App

A native iOS application for connecting to and monitoring SwitchBot leak detection sensors via Bluetooth Low Energy (BLE).

## Features

- **Bluetooth Device Discovery**: Automatically scans for and identifies SwitchBot devices
- **Target Device Recognition**: Specifically targets the SwitchBot leak detector with MAC address `ECD25189-92D0-6712-8C02-86B4D17BA636`
- **Real-time Connection**: Establishes persistent BLE connections to leak sensors
- **Service Discovery**: Automatically discovers all available BLE services and characteristics
- **Data Interpretation**: Interprets SwitchBot-specific data formats including:
  - Leak detection status (leak detected/no leak)
  - Temperature readings
  - Battery level
  - Manufacturer information
- **Live Monitoring**: Receives real-time notifications from connected sensors
- **Activity Logging**: Comprehensive logging of all Bluetooth operations and sensor data
- **Device Profile Storage**: Saves device information for future connections

## Requirements

- iOS 13.0 or later
- iPhone or iPad with Bluetooth Low Energy support
- SwitchBot leak detector device

## Setup Instructions

### 1. Build and Run
1. Open the project in Xcode
2. Select your target device or simulator
3. Build and run the application

### 2. Bluetooth Permissions
The app will request Bluetooth permissions when first launched. Grant the necessary permissions:
- **Always Allow**: For background monitoring
- **While Using**: For active monitoring during app use

### 3. Using the App

#### Scanning for Devices
1. Tap "Start Scan" to begin searching for Bluetooth devices
2. The app will automatically filter for SwitchBot devices
3. Your target leak detector will be highlighted with a 🎯 icon
4. Scanning automatically stops after 10 seconds

#### Connecting to a Device
1. Select a device from the discovered devices list
2. Tap "Connect" to establish a connection
3. The app will automatically discover services and characteristics
4. Once connected, the button changes to "Disconnect"

#### Monitoring Sensor Data
- Once connected, the app automatically subscribes to sensor notifications
- Real-time data appears in the activity log
- Leak detection events are clearly marked with 🚨
- Temperature and battery data are interpreted and displayed

## Technical Details

### Target Device Specifications
- **MAC Address**: `ECD25189-92D0-6712-8C02-86B4D17BA636`
- **Service UUID**: `0000fd3d-0000-1000-8000-00805f9b34fb`
- **Device Type**: SwitchBot Leak Detector

### Data Interpretation
The app interprets SwitchBot-specific data formats:

#### Leak Detection
- `0x00`: No leak detected
- `0x01`: **LEAK DETECTED** 🚨

#### Temperature Data
- Format: `0x57` prefix followed by temperature bytes
- Temperature calculation: `Int16(data[2]) | (Int16(data[3]) << 8) / 10.0`

#### Standard GATT Characteristics
- **Battery Level** (`2a19`): Battery percentage
- **Manufacturer Name** (`2a29`): Device manufacturer
- **Model Number** (`2a24`): Device model
- **Firmware Revision** (`2a26`): Firmware version

### Background Operation
The app supports background Bluetooth operations for continuous monitoring:
- Configured for `bluetooth-central` and `bluetooth-peripheral` background modes
- Maintains connections when app is in background
- Continues receiving sensor notifications

## Troubleshooting

### Common Issues

1. **Device Not Found**
   - Ensure the SwitchBot device is powered on
   - Check that Bluetooth is enabled on your iOS device
   - Try moving closer to the device
   - Restart the SwitchBot device if necessary

2. **Connection Fails**
   - Verify the device is not connected to another app
   - Check that the device is in pairing mode if required
   - Ensure the device is within range

3. **No Data Received**
   - Verify the connection is established
   - Check that notifications are enabled for the characteristics
   - Trigger the sensor manually (e.g., with a wet finger for leak detection)

### Debug Information
The app provides comprehensive logging in the activity log:
- Bluetooth state changes
- Device discovery events
- Connection attempts and results
- Service and characteristic discovery
- Real-time sensor data

## Development Notes

### Architecture
- **ViewController**: Main UI controller with Bluetooth functionality
- **CBCentralManager**: Manages Bluetooth scanning and connections
- **CBPeripheralDelegate**: Handles device communication
- **Core Data**: Stores device profiles and sensor data

### Key Components
- `ViewController.swift`: Main application logic
- `Main.storyboard`: User interface layout
- `Info.plist`: Bluetooth permissions and background modes

### Extending the App
The app is designed to be easily extensible:
- Add support for additional SwitchBot devices
- Implement data persistence with Core Data
- Add push notifications for leak events
- Create a widget for quick status checking

## Privacy and Security
- The app only connects to authorized SwitchBot devices
- No data is transmitted to external servers
- All sensor data is stored locally on the device
- Bluetooth permissions are clearly explained to users

## Support
For technical support or feature requests, please refer to the project documentation or contact the development team. 