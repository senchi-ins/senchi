# Senchi IoT Connection App

A comprehensive iOS application for managing IoT devices, with a focus on water leak detection and home automation.

## Features

### Bluetooth Device Management
- **Device Discovery**: Scan for and discover nearby Bluetooth devices
- **Targeted Scanning**: Focus on specific device types (WoSenW devices)
- **Connection Management**: Connect to and manage discovered devices
- **Data Transfer**: Send and receive data from connected devices
- **Status Monitoring**: Real-time device status and health monitoring

### Home Automation System
The app now includes a comprehensive home automation interface that provides the same functionality as the web-based dashboard:

#### Real-time Device Monitoring
- **WebSocket Connection**: Real-time connection to the home automation server
- **Device Status Display**: View water leak status, battery levels, signal quality, and temperature
- **Automatic Reconnection**: Handles connection drops with exponential backoff
- **Connection Health**: Visual indicators for API and WebSocket status

#### Alert System
- **Water Leak Alerts**: Immediate notifications when water leaks are detected
- **Low Battery Warnings**: Alerts for devices with low battery levels
- **Device Status Changes**: Notifications when devices come back online
- **Push Notifications**: Local notifications for critical alerts
- **In-App Alerts**: Modal alerts for immediate attention

#### Device Management
- **Device Pairing**: Enable pairing mode for adding new devices
- **Device List**: Real-time list of all connected devices
- **Status Indicators**: Color-coded status for different device conditions
- **Last Seen Tracking**: Monitor when devices were last active

#### Control Features
- **Add Device**: Enable pairing mode for new device discovery
- **Test Alerts**: Test the notification system
- **Clear Logs**: Clear the activity log
- **Real-time Logs**: Live activity monitoring with timestamps

## Architecture

### Core Components

1. **BluetoothManager**: Handles all Bluetooth Low Energy operations
2. **HomeAutomationViewController**: Main interface for home automation features
3. **DeviceTableViewCell**: Custom cell for displaying device information
4. **WebSocketManager**: Manages real-time communication with the server

### Data Models

- **IoTDevice**: Represents a connected IoT device with status information
- **DeviceStatus**: Contains device sensor data (water leak, battery, temperature, etc.)
- **WebSocketMessage**: Handles communication protocol with the server

### Network Communication

The app connects to the home automation server at `wss://senchi-mqtt.up.railway.app/ws` for real-time updates and `https://senchi-mqtt.up.railway.app/zigbee/permit-join` for device pairing.

## Usage

### Getting Started

1. **Launch the App**: Open the Senchi app on your iOS device
2. **Bluetooth Setup**: Ensure Bluetooth is enabled and permissions are granted
3. **Access Home Automation**: Tap the "🏠 Home Automation" button on the main screen

### Home Automation Interface

1. **Connection Status**: Monitor the connection status at the top of the screen
2. **Device List**: View all connected devices with their current status
3. **Controls**: Use the control buttons to manage the system
4. **Logs**: Monitor real-time activity in the log section

### Device Management

1. **Add New Device**: Tap "Add Device" to enable pairing mode
2. **Monitor Status**: Watch for alerts and status changes
3. **Test System**: Use "Test Alert" to verify notifications are working

## Technical Details

### WebSocket Protocol

The app communicates with the server using a JSON-based WebSocket protocol:

```json
{
  "type": "device_update",
  "device_id": "device123",
  "data": {
    "water_leak": false,
    "battery": 85,
    "battery_low": false,
    "linkquality": 120,
    "device_temperature": 23.5
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Alert Types

- **Error**: Critical alerts (water leaks, system failures)
- **Warning**: Important warnings (low battery, poor signal)
- **Success**: Positive notifications (device back online)
- **Info**: General information messages

### Permissions Required

- **Bluetooth**: For device discovery and communication
- **Notifications**: For alert delivery
- **Network**: For WebSocket and API communication

## Development

### Building the App

1. Open the project in Xcode
2. Ensure all dependencies are installed
3. Build and run on a physical device (Bluetooth features require hardware)

### Key Files

- `ViewController.swift`: Main Bluetooth interface
- `HomeAutomationViewController.swift`: Home automation interface
- `BluetoothManager.swift`: Bluetooth communication logic
- `Main.storyboard`: User interface layout

### Testing

- Use the "Test Alert" button to verify notification functionality
- Monitor the logs for connection and communication status
- Test device pairing with actual IoT devices

## Troubleshooting

### Common Issues

1. **Connection Failures**: Check network connectivity and server status
2. **Bluetooth Issues**: Ensure Bluetooth is enabled and permissions granted
3. **Notification Problems**: Verify notification permissions in Settings
4. **Device Not Found**: Check device compatibility and pairing mode

### Debug Information

The app includes comprehensive logging that can help diagnose issues:
- WebSocket connection status
- Device discovery and updates
- Alert generation and delivery
- API call results

## Future Enhancements

- **Device Configuration**: Advanced device settings and configuration
- **Historical Data**: View device history and trends
- **Automation Rules**: Create custom automation rules
- **Multi-User Support**: Share devices between users
- **Offline Mode**: Local device management when offline 