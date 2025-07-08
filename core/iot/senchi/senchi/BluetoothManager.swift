//
//  BluetoothManager.swift
//  senchi
//
//  Created by Michael Dawes on 2025-06-30.
//

import Foundation
import CoreBluetooth
import os

// Import TransferService from the same module

protocol BluetoothManagerDelegate: AnyObject {
    func bluetoothManager(_ manager: BluetoothManager, didUpdateState state: CBManagerState)
    func bluetoothManager(_ manager: BluetoothManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi: NSNumber)
    func bluetoothManager(_ manager: BluetoothManager, didConnect peripheral: CBPeripheral)
    func bluetoothManager(_ manager: BluetoothManager, didFailToConnect peripheral: CBPeripheral, error: Error?)
    func bluetoothManager(_ manager: BluetoothManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?)
    func bluetoothManager(_ manager: BluetoothManager, didReceiveData data: Data, from characteristic: CBCharacteristic, interpretation: String)
    func bluetoothManager(_ manager: BluetoothManager, didLog message: String)
    func bluetoothManager(_ manager: BluetoothManager, didReceiveTransferData data: Data)
    func bluetoothManager(_ manager: BluetoothManager, didSendTransferData data: Data)
}



class BluetoothManager: NSObject {
    
    // MARK: - Properties
    weak var delegate: BluetoothManagerDelegate?
    private var centralManager: CBCentralManager!
    private var peripheralManager: CBPeripheralManager!
    private var connectedPeripheral: CBPeripheral?
    private var discoveredDevices: [CBPeripheral] = []
    
    // MARK: - Transfer Service Properties
    private var transferCharacteristic: CBMutableCharacteristic?
    private var connectedCentral: CBCentral?
    private var dataToSend = Data()
    private var sendDataIndex: Int = 0
    private static var sendingEOM = false
    
    // MARK: - Device Specific Constants (Legacy Support)
    private let targetDeviceName = "WoSenW"
    private let targetServiceUUID = CBUUID(string: "CBA20D00-224D-11E6-9FB8-0002A5D5C51B")
    private let notifyCharacteristicUUID = CBUUID(string: "CBA20003-224D-11E6-9FB8-0002A5D5C51B")
    private let writeCharacteristicUUID = CBUUID(string: "CBA20002-224D-11E6-9FB8-0002A5D5C51B")
    

    
    // MARK: - Data Storage
    private var deviceProfile: [String: Any] = [:]
    private var notificationHistory: [[String: Any]] = []
    private var receivedData = Data()
    
    // MARK: - Configuration
//    var mode: BluetoothMode = .both
    
    // MARK: - Connection Maintenance
    private var keepAliveTimer: Timer?
    private var reconnectTimer: Timer?
    private var connectionAttempts = 0
    private let maxReconnectAttempts = 5
    private let keepAliveInterval: TimeInterval = 10.0 // Send keep-alive every 10 seconds
    private let reconnectInterval: TimeInterval = 2.0 // Try to reconnect every 2 seconds
    
    // MARK: - Handshake and Pairing
    private var handshakeCompleted = false
    private var pairingSequence: [Data] = []
    private var currentPairingStep = 0
    private var handshakeTimer: Timer?
    
    // Common handshake sequences for leak detectors
    private let handshakeSequences: [String: [Data]] = [
        "WoSenW": [
            Data([0x01, 0x00]), // Initiate pairing
            Data([0x02, 0x01]), // Confirm pairing
            Data([0x03, 0x00]), // Request device info
            Data([0x04, 0x01]), // Enable notifications
            Data([0x05, 0x00])  // Complete handshake
        ],
        "Generic": [
            Data([0xAA, 0x55]), // Standard BLE handshake
            Data([0x55, 0xAA]), // Response
            Data([0x01, 0x01])  // Enable notifications
        ]
    ]
    
    // MARK: - Initialization
    override init() {
        super.init()
        setupBluetoothManager()
    }
    
    private func setupBluetoothManager() {
        centralManager = CBCentralManager(delegate: self, queue: nil)
        peripheralManager = CBPeripheralManager(delegate: self, queue: nil, options: [CBPeripheralManagerOptionShowPowerAlertKey: true])
        log("Bluetooth manager initialized")
    }
    
    // MARK: - Public Methods
    
    // MARK: Central Mode Methods
    func startScanning() {
        guard centralManager.state == .poweredOn else {
            log("Bluetooth is not available")
            return
        }
        discoveredDevices.removeAll()
        
        // Start with broad scanning to see all devices
        log("Starting broad scan to identify all advertising devices...")
        centralManager.scanForPeripherals(withServices: nil, options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
        
        log("Started scanning for Bluetooth devices...")
    }
    
    func startTargetedScanning() {
        guard centralManager.state == .poweredOn else {
            log("Bluetooth is not available")
            return
        }
        discoveredDevices.removeAll()
        
        // Scan for specific services
        let servicesToScan = [targetServiceUUID]
        log("Starting targeted scan for services: \(servicesToScan.map { $0.uuidString })")
        centralManager.scanForPeripherals(withServices: servicesToScan, options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
        
        log("Started targeted scanning...")
    }
    
    func stopScanning() {
        centralManager.stopScan()
        log("Stopped scanning. Found \(discoveredDevices.count) devices")
    }
    
    func connect(to peripheral: CBPeripheral) {
        log("Attempting to connect to: \(peripheral.name ?? "Unknown")")
        connectedPeripheral = peripheral
        centralManager.connect(peripheral, options: nil)
    }
    
    func disconnect() {
        guard let peripheral = connectedPeripheral else { return }
        
        stopKeepAlive()
        stopReconnectTimer()
        
        centralManager.cancelPeripheralConnection(peripheral)
        connectedPeripheral = nil
        log("Disconnected from device")
    }
    
    // MARK: Peripheral Mode Methods
//    func startAdvertising() {
//        guard peripheralManager.state == .poweredOn else {
//            log("Peripheral manager not ready")
//            return
//        }
//        
//        setupPeripheral()
//        peripheralManager.startAdvertising([CBAdvertisementDataServiceUUIDsKey: [TransferService.serviceUUID]])
//        log("Started advertising transfer service")
//    }
    
    func stopAdvertising() {
        peripheralManager.stopAdvertising()
        log("Stopped advertising")
    }
    
    func sendData(_ data: Data) {
        dataToSend = data
        sendDataIndex = 0
        BluetoothManager.sendingEOM = false
        sendData()
    }
    
    // MARK: Utility Methods
    func getDiscoveredDevices() -> [CBPeripheral] {
        return discoveredDevices
    }
    
    func isConnected() -> Bool {
        return connectedPeripheral?.state == .connected
    }
    
    func getDeviceProfile() -> [String: Any] {
        return deviceProfile
    }
    
    func getNotificationHistory() -> [[String: Any]] {
        return notificationHistory
    }
    
    func getReceivedData() -> Data {
        return receivedData
    }
    
    // MARK: - Event Detection Methods
    func requestDeviceStatus() {
        guard let peripheral = connectedPeripheral,
              peripheral.state == .connected else {
            log("Cannot request status - not connected")
            return
        }
        
        log("Requesting device status...")
        
        // Read all readable characteristics to get current status
        if let services = peripheral.services {
            for service in services {
                if let characteristics = service.characteristics {
                    for characteristic in characteristics {
                        if characteristic.properties.contains(.read) {
                            log("Reading characteristic: \(characteristic.uuid)")
                            peripheral.readValue(for: characteristic)
                        }
                    }
                }
            }
        }
    }
    
    func enableEventNotifications() {
        guard let peripheral = connectedPeripheral,
              peripheral.state == .connected else {
            log("Cannot enable notifications - not connected")
            return
        }
        
        log("Enabling event notifications...")
        
        // Subscribe to all notifiable characteristics
        if let services = peripheral.services {
            for service in services {
                if let characteristics = service.characteristics {
                    for characteristic in characteristics {
                        if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
                            log("Enabling notifications for: \(characteristic.uuid)")
                            peripheral.setNotifyValue(true, for: characteristic)
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Connection Maintenance Methods
    private func startKeepAlive() {
        stopKeepAlive() // Stop any existing timer
        
        keepAliveTimer = Timer.scheduledTimer(withTimeInterval: keepAliveInterval, repeats: true) { [weak self] _ in
            self?.sendKeepAlive()
        }
        
        log("Started keep-alive timer (every \(keepAliveInterval) seconds)")
    }
    
    private func stopKeepAlive() {
        keepAliveTimer?.invalidate()
        keepAliveTimer = nil
    }
    
    private func sendKeepAlive() {
        guard let peripheral = connectedPeripheral,
              peripheral.state == .connected else {
            log("Cannot send keep-alive - not connected")
            return
        }
        
        // Send a simple ping to keep the connection alive
        let pingData = "PING".data(using: .utf8)!
        log("Sending keep-alive ping")
        
        // Try to write to a characteristic to maintain connection
        if let writeCharacteristic = findWriteCharacteristic() {
            peripheral.writeValue(pingData, for: writeCharacteristic, type: .withResponse)
        }
    }
    
    private func findWriteCharacteristic() -> CBCharacteristic? {
        guard let peripheral = connectedPeripheral,
              let services = peripheral.services else { return nil }
        
        for service in services {
            if let characteristics = service.characteristics {
                for characteristic in characteristics {
                    if characteristic.properties.contains(.write) || characteristic.properties.contains(.writeWithoutResponse) {
                        return characteristic
                    }
                }
            }
        }
        return nil
    }
    
    private func startReconnectTimer() {
        stopReconnectTimer()
        
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: reconnectInterval, repeats: true) { [weak self] _ in
            self?.attemptReconnection()
        }
        
        log("Started reconnection timer (every \(reconnectInterval) seconds)")
    }
    
    private func stopReconnectTimer() {
        reconnectTimer?.invalidate()
        reconnectTimer = nil
    }
    
    private func attemptReconnection() {
        guard let peripheral = connectedPeripheral else {
            stopReconnectTimer()
            return
        }
        
        connectionAttempts += 1
        
        if connectionAttempts > maxReconnectAttempts {
            log("Max reconnection attempts reached. Giving up.")
            stopReconnectTimer()
            delegate?.bluetoothManager(self, didDisconnectPeripheral: peripheral, error: nil)
            return
        }
        
        log("Attempting reconnection #\(connectionAttempts)/\(maxReconnectAttempts)")
        centralManager.connect(peripheral, options: nil)
    }
    
    // MARK: - Private Methods
    private func log(_ message: String) {
        delegate?.bluetoothManager(self, didLog: message)
    }
    
//    private func discoverServices(for peripheral: CBPeripheral) {
//        log("Discovering services...")
//        peripheral.delegate = self
//        peripheral.discoverServices([targetServiceUUID, TransferService.serviceUUID])
//    }
//    
//    private func discoverCharacteristics(for service: CBService) {
//        log("Discovering characteristics for service: \(service.uuid)")
//        
//        if service.uuid == TransferService.serviceUUID {
//            service.peripheral?.discoverCharacteristics([TransferService.characteristicUUID], for: service)
//        } else {
//            service.peripheral?.discoverCharacteristics([notifyCharacteristicUUID, writeCharacteristicUUID], for: service)
//        }
//    }
    
    private func interpretData(_ data: Data, for characteristic: CBCharacteristic) -> String {
        let hexString = data.map { String(format: "%02x", $0) }.joined()
        
        // Enhanced interpretation for leak detection events
        if data.count >= 1 {
            let firstByte = data[0]
            
            // Check for common event patterns
            switch firstByte {
            case 0x01:
                return "🚨 LEAK DETECTED! - Sensor triggered"
            case 0x02:
                return "✅ LEAK CLEARED - Sensor reset"
            case 0x03:
                return "🔋 LOW BATTERY - Device needs charging"
            case 0x04:
                return "📡 HEARTBEAT - Device status update"
            case 0x05:
                return "🔧 SENSOR ERROR - Device malfunction"
            case 0x06:
                return "🌊 WATER DETECTED - Moisture sensor active"
            case 0x07:
                return "🔒 TAMPER ALERT - Device tampering detected"
            case 0x57:
                return "📡 PING RESPONSE - Sensor status received"
            default:
                // Try to interpret as text
                if let text = String(data: data, encoding: .utf8) {
                    return "📝 Text message: \(text)"
                }
                return "📊 Raw data: \(hexString)"
            }
        }
        
        return "📊 Data: \(hexString)"
    }
    
    private func saveDeviceProfile() {
        guard let peripheral = connectedPeripheral else { return }
        
        deviceProfile = [
            "mac_address": targetDeviceName,
            "device_name": peripheral.name ?? "Unknown",
            "device_identifier": peripheral.identifier.uuidString,
            "connection_timestamp": Date().timeIntervalSince1970,
            "notification_count": notificationHistory.count
        ]
        
        log("Device profile saved")
    }
    
    private func addNotification(_ data: Data, characteristic: CBCharacteristic, interpretation: String) {
        let notification: [String: Any] = [
            "timestamp": Date().timeIntervalSince1970,
            "characteristic": characteristic.uuid.uuidString,
            "data": data.map { String(format: "%02x", $0) }.joined(),
            "interpretation": interpretation
        ]
        
        notificationHistory.append(notification)
    }
    
    // MARK: - Transfer Service Methods
//    private func setupPeripheral() {
//        let transferCharacteristic = CBMutableCharacteristic(
//            type: TransferService.characteristicUUID,
//            properties: [.notify, .writeWithoutResponse],
//            value: nil,
//            permissions: [.readable, .writeable]
//        )
//        
//        let transferService = CBMutableService(type: TransferService.serviceUUID, primary: true)
//        transferService.characteristics = [transferCharacteristic]
//        
//        peripheralManager.add(transferService)
//        self.transferCharacteristic = transferCharacteristic
//        log("Transfer service setup complete")
//    }
    
    private func sendData() {
        guard let transferCharacteristic = transferCharacteristic else {
            return
        }
        
        // First up, check if we're meant to be sending an EOM
        if BluetoothManager.sendingEOM {
            let didSend = peripheralManager.updateValue("EOM".data(using: .utf8)!, for: transferCharacteristic, onSubscribedCentrals: nil)
            if didSend {
                BluetoothManager.sendingEOM = false
                log("Sent: EOM")
                delegate?.bluetoothManager(self, didSendTransferData: dataToSend)
            }
            return
        }
        
        // We're not sending an EOM, so we're sending data
        if sendDataIndex >= dataToSend.count {
            return
        }
        
        // There's data left, so send until the callback fails, or we're done.
        var didSend = true
        while didSend {
            var amountToSend = dataToSend.count - sendDataIndex
            if let mtu = connectedCentral?.maximumUpdateValueLength {
                amountToSend = min(amountToSend, mtu)
            }
            
            let chunk = dataToSend.subdata(in: sendDataIndex..<(sendDataIndex + amountToSend))
            didSend = peripheralManager.updateValue(chunk, for: transferCharacteristic, onSubscribedCentrals: nil)
            
            if !didSend {
                return
            }
            
            let stringFromData = String(data: chunk, encoding: .utf8)
            log("Sent \(chunk.count) bytes: \(stringFromData ?? "unknown")")
            
            sendDataIndex += amountToSend
            
            if sendDataIndex >= dataToSend.count {
                BluetoothManager.sendingEOM = true
                let eomSent = peripheralManager.updateValue("EOM".data(using: .utf8)!, for: transferCharacteristic, onSubscribedCentrals: nil)
                
                if eomSent {
                    BluetoothManager.sendingEOM = false
                    log("Sent: EOM")
                    delegate?.bluetoothManager(self, didSendTransferData: dataToSend)
                }
                return
            }
        }
    }
}

// MARK: - CBCentralManagerDelegate
extension BluetoothManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        delegate?.bluetoothManager(self, didUpdateState: central.state)
        
        switch central.state {
        case .poweredOn:
            log("Bluetooth is powered on and ready")
        case .poweredOff:
            log("Bluetooth is powered off")
        case .unauthorized:
            log("Bluetooth access denied")
        case .unsupported:
            log("Bluetooth is not supported")
        case .resetting:
            log("Bluetooth is resetting")
        case .unknown:
            log("Bluetooth state is unknown")
        @unknown default:
            log("Unknown Bluetooth state")
        }
    }
    
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        // Log all discovered devices for debugging
        log("Discovered device: \(peripheral.name ?? "Unknown") - RSSI: \(RSSI)")
        
        // Extract and log all advertised services
        let advertisedServices = advertisementData[CBAdvertisementDataServiceUUIDsKey] as? [CBUUID] ?? []
        let serviceNames = advertisedServices.map { $0.uuidString }
        log("  Advertised services: \(serviceNames)")
        
        // Check for both legacy devices and transfer service devices
        let isTargetDevice = peripheral.name == targetDeviceName
        let hasTargetService = advertisedServices.contains(targetServiceUUID)
        // let hasTransferService = advertisedServices.contains(TransferService.serviceUUID) // Temporarily commented
        
        log("  Device analysis: isTarget=\(isTargetDevice), hasTarget=\(hasTargetService)")
        
        // Accept devices that match any of our criteria
        if isTargetDevice || hasTargetService {
            if !discoveredDevices.contains(where: { $0.identifier == peripheral.identifier }) {
                discoveredDevices.append(peripheral)
                log("✅ Added device: \(peripheral.name ?? "Unknown") (\(peripheral.identifier))")
                delegate?.bluetoothManager(self, didDiscover: peripheral, advertisementData: advertisementData, rssi: RSSI)
            } else {
                log("  Device already in list: \(peripheral.name ?? "Unknown")")
            }
        } else {
            log("❌ Device rejected: \(peripheral.name ?? "Unknown") - doesn't match criteria")
        }
    }
    
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        log("Successfully connected to \(peripheral.name ?? "device")")
        
        // Reset connection attempts and start keep-alive
        connectionAttempts = 0
        stopReconnectTimer()
        startKeepAlive()
        
        delegate?.bluetoothManager(self, didConnect: peripheral)
//        discoverServices(for: peripheral)
    }
    
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        log("Failed to connect: \(error?.localizedDescription ?? "Unknown error")")
        
        // Start reconnection timer if this is our target peripheral
        if peripheral == connectedPeripheral {
            startReconnectTimer()
        }
        
        delegate?.bluetoothManager(self, didFailToConnect: peripheral, error: error)
    }
    
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        log("Disconnected from \(peripheral.name ?? "device")")
        
        // Stop keep-alive and start reconnection if this is our target peripheral
        if peripheral == connectedPeripheral {
            stopKeepAlive()
            startReconnectTimer()
        }
        
        delegate?.bluetoothManager(self, didDisconnectPeripheral: peripheral, error: error)
    }
}

// MARK: - CBPeripheralManagerDelegate
extension BluetoothManager: CBPeripheralManagerDelegate {
    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        switch peripheral.state {
        case .poweredOn:
            log("Peripheral manager is powered on")
        case .poweredOff:
            log("Peripheral manager is powered off")
        case .unauthorized:
            log("Peripheral manager access denied")
        case .unsupported:
            log("Peripheral manager is not supported")
        case .resetting:
            log("Peripheral manager is resetting")
        case .unknown:
            log("Peripheral manager state is unknown")
        @unknown default:
            log("Unknown peripheral manager state")
        }
    }
    
    func peripheralManagerIsReady(toUpdateSubscribers peripheral: CBPeripheralManager) {
        sendData()
    }
    
    func peripheralManager(_ peripheral: CBPeripheralManager, didReceiveWrite requests: [CBATTRequest]) {
        for request in requests {
            if let data = request.value {
                let stringFromData = String(data: data, encoding: .utf8)
                log("Received write request: \(stringFromData ?? "unknown")")
                
                if stringFromData == "EOM" {
                    // End of message received
                    log("Received complete transfer data")
                    delegate?.bluetoothManager(self, didReceiveTransferData: receivedData)
                    receivedData.removeAll(keepingCapacity: false)
                } else {
                    // Append data to received buffer
                    receivedData.append(data)
                }
            }
            peripheral.respond(to: request, withResult: .success)
        }
    }
}

// MARK: - CBPeripheralDelegate
//extension BluetoothManager: CBPeripheralDelegate {
//    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
//        if let error = error {
//            log("Service discovery failed: \(error.localizedDescription)")
//            return
//        }
//        
//        guard let services = peripheral.services else { return }
//        
//        log("Discovered \(services.count) services")
//        
//        for service in services {
//            log("Service: \(service.uuid)")
////            discoverCharacteristics(for: service)
//        }
//    }
    
//    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
//        if let error = error {
//            log("Characteristic discovery failed: \(error.localizedDescription)")
//            return
//        }
//        
//        guard let characteristics = service.characteristics else { return }
//        
//        log("Discovered \(characteristics.count) characteristics for service \(service.uuid)")
//        
//        for characteristic in characteristics {
//            log("Characteristic: \(characteristic.uuid) - Properties: \(characteristic.properties)")
//            
//            // Handle transfer service characteristic
//            if characteristic.uuid == TransferService.characteristicUUID {
//                if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
//                    peripheral.setNotifyValue(true, for: characteristic)
//                    log("Subscribed to transfer service notifications")
//                }
//            } else {
//                // Handle legacy characteristics
//                if characteristic.properties.contains(.read) {
//                    peripheral.readValue(for: characteristic)
//                }
//                
//                if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
//                    peripheral.setNotifyValue(true, for: characteristic)
//                    log("Subscribed to notifications for \(characteristic.uuid)")
//                }
//            }
//        }
        
        // Save device profile after discovering all characteristics
//        saveDeviceProfile()
//    }
    
//    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
//        if let error = error {
//            log("Value update failed: \(error.localizedDescription)")
//            return
//        }
//        
//        guard let data = characteristic.value else { return }
//        
//        // Check if this is a handshake response first
//        if !handshakeCompleted && isValidHandshakeResponse(data) {
//            handleHandshakeResponse(data, from: characteristic)
//            return
//        }
//        
//        // Handle transfer service data
//        if characteristic.uuid == TransferService.characteristicUUID {
//            let stringFromData = String(data: data, encoding: .utf8)
//            log("Received transfer data: \(stringFromData ?? "unknown")")
//            
//            if stringFromData == "EOM" {
//                // End of message received
//                log("Received complete transfer data")
//                delegate?.bluetoothManager(self, didReceiveTransferData: receivedData)
//                receivedData.removeAll(keepingCapacity: false)
//            } else {
//                // Append data to received buffer
//                receivedData.append(data)
//            }
//        } else {
//            // Handle legacy data
//            let interpretation = interpretData(data, for: characteristic)
//            addNotification(data, characteristic: characteristic, interpretation: interpretation)
//            
//            log("📡 \(interpretation)")
//            delegate?.bluetoothManager(self, didReceiveData: data, from: characteristic, interpretation: interpretation)
//        }
//    }
    
//    func peripheral(_ peripheral: CBPeripheral, didReadRSSI RSSI: NSNumber, error: Error?) {
//        if let error = error {
//            log("RSSI read failed: \(error.localizedDescription)")
//        } else {
//            log("RSSI: \(RSSI) dBm")
//        }
//    }
//}

// MARK: - Handshake and Pairing Methods
extension BluetoothManager {
    
    /// Initiates the handshake sequence with the connected device
    func initiateHandshake() {
        guard let peripheral = connectedPeripheral else {
            log("❌ No device connected for handshake")
            return
        }
        
        log("🤝 Starting handshake sequence with \(peripheral.name ?? "device")")
        handshakeCompleted = false
        currentPairingStep = 0
        
        // Determine which handshake sequence to use based on device name
        let deviceName = peripheral.name ?? ""
        if deviceName.contains("WoSenW") || deviceName.contains("WoSen") {
            pairingSequence = handshakeSequences["WoSenW"] ?? handshakeSequences["Generic"]!
            log("Using WoSenW handshake sequence")
        } else {
            pairingSequence = handshakeSequences["Generic"]!
            log("Using generic handshake sequence")
        }
        
        // Start the handshake process
        performNextHandshakeStep()
    }
    
    /// Performs the next step in the handshake sequence
    private func performNextHandshakeStep() {
        guard currentPairingStep < pairingSequence.count else {
            log("✅ Handshake sequence completed")
            handshakeCompleted = true
            return
        }
        
        let handshakeData = pairingSequence[currentPairingStep]
        log("🤝 Handshake step \(currentPairingStep + 1)/\(pairingSequence.count): \(handshakeData.map { String(format: "%02X", $0) }.joined())")
        
        // Send the handshake data
        sendHandshakeData(handshakeData)
        
        // Set a timer for the next step (give device time to respond)
        handshakeTimer?.invalidate()
        handshakeTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: false) { [weak self] _ in
            self?.currentPairingStep += 1
            self?.performNextHandshakeStep()
        }
    }
    
    /// Sends handshake data to the device
    private func sendHandshakeData(_ data: Data) {
        guard let peripheral = connectedPeripheral else { return }
        
        // Try to find a writable characteristic
        for service in peripheral.services ?? [] {
            for characteristic in service.characteristics ?? [] {
                if characteristic.properties.contains(.write) || characteristic.properties.contains(.writeWithoutResponse) {
                    peripheral.writeValue(data, for: characteristic, type: .withResponse)
                    log("📤 Sent handshake data to \(characteristic.uuid)")
                    return
                }
            }
        }
        
        log("❌ No writable characteristic found for handshake")
    }
    
    /// Handles incoming handshake responses
    private func handleHandshakeResponse(_ data: Data, from characteristic: CBCharacteristic) {
        log("📥 Handshake response: \(data.map { String(format: "%02X", $0) }.joined())")
        
        // Check if this is a valid handshake response
        if isValidHandshakeResponse(data) {
            log("✅ Valid handshake response received")
            // Continue with next step immediately
            handshakeTimer?.invalidate()
            currentPairingStep += 1
            performNextHandshakeStep()
        } else {
            log("⚠️ Unexpected handshake response, continuing with timer")
        }
    }
    
    /// Validates handshake response data
    private func isValidHandshakeResponse(_ data: Data) -> Bool {
        guard data.count >= 2 else { return false }
        
        // Check for common response patterns
        let firstByte = data[0]
        let secondByte = data[1]
        
        // WoSenW response patterns
        if firstByte == 0x01 && secondByte == 0x01 { return true } // Acknowledge
        if firstByte == 0x02 && secondByte == 0x00 { return true } // Confirm
        if firstByte == 0x03 && secondByte == 0x01 { return true } // Info response
        if firstByte == 0x04 && secondByte == 0x00 { return true } // Notification enabled
        if firstByte == 0x05 && secondByte == 0x01 { return true } // Handshake complete
        
        // Generic response patterns
        if firstByte == 0x55 && secondByte == 0xAA { return true } // Standard response
        if firstByte == 0x01 && secondByte == 0x01 { return true } // Generic acknowledge
        
        return false
    }
    
    /// Requests device pairing with authentication
    func requestPairing() {
//        guard let peripheral = connectedPeripheral else {
//            log("❌ No device connected for pairing")
//            return
//        }
        
        log("🔐 Requesting device pairing...")
        
        // Send pairing request with device-specific authentication
        let pairingRequest = createPairingRequest()
        sendHandshakeData(pairingRequest)
        
        // Set up pairing response handler
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
            self?.log("⏰ Checking for pairing response...")
        }
    }
    
    /// Creates a device-specific pairing request
    private func createPairingRequest() -> Data {
        // WoSenW specific pairing request
        var request = Data()
        request.append(0x50) // Pairing command
        request.append(0x01) // Request type
        request.append(0x00) // Reserved
        request.append(0x00) // Reserved
        
        // Add device identifier if available
        if let peripheral = connectedPeripheral {
            let deviceId = peripheral.identifier.uuidString.prefix(8)
            if let deviceIdData = deviceId.data(using: .utf8) {
                request.append(deviceIdData)
            }
        }
        
        return request
    }
    
    /// Completes the pairing process
    func completePairing() {
        guard handshakeCompleted else {
            log("❌ Handshake not completed, cannot finish pairing")
            return
        }
        
        log("✅ Pairing completed successfully")
        
        // Enable all notifications
        enableAllNotifications()
        
        // Request device status
        requestDeviceStatus()
        
        // Start monitoring for events
        startEventMonitoring()
    }
    
    /// Enables all available notifications
    private func enableAllNotifications() {
        guard let peripheral = connectedPeripheral else { return }
        
        log("🔔 Enabling all notifications...")
        
        for service in peripheral.services ?? [] {
            for characteristic in service.characteristics ?? [] {
                if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
                    peripheral.setNotifyValue(true, for: characteristic)
                    log("✅ Enabled notifications for \(characteristic.uuid)")
                }
            }
        }
    }
    
    /// Requests current device status via handshake
    func requestDeviceStatusViaHandshake() {
        let statusRequest = Data([0x53, 0x54, 0x41, 0x54]) // "STAT"
        sendHandshakeData(statusRequest)
        log("📊 Requested device status via handshake")
    }
    
    /// Starts monitoring for device events
    private func startEventMonitoring() {
        log("👁️ Started event monitoring")
        
        // Send event monitoring command
        let monitorCommand = Data([0x4D, 0x4F, 0x4E, 0x49]) // "MONI"
        sendHandshakeData(monitorCommand)
    }
    
    /// Checks if handshake is completed
    func isHandshakeCompleted() -> Bool {
        return handshakeCompleted
    }
    
    /// Resets handshake state
    func resetHandshake() {
        handshakeCompleted = false
        currentPairingStep = 0
        handshakeTimer?.invalidate()
        handshakeTimer = nil
        log("🔄 Handshake state reset")
    }
    
    /// Pings the sensor to get current status (matches Python implementation)
    func pingSensor() {
        guard let peripheral = connectedPeripheral,
              peripheral.state == .connected else {
            log("❌ Cannot ping sensor - not connected")
            return
        }
        
        log("📡 Pinging sensor...")
        
        // Create ping data: 0x57 0x02 (matches Python implementation)
        let pingData = Data([0x57, 0x02])
        log("📤 Sending ping command: \(pingData.map { String(format: "%02X", $0) }.joined())")
        
        // Find writable characteristic and send ping
        if let writeCharacteristic = findWriteCharacteristic() {
            peripheral.writeValue(pingData, for: writeCharacteristic, type: .withResponse)
            log("✅ Ping command sent to \(writeCharacteristic.uuid)")
        } else {
            log("❌ No writable characteristic found for ping")
        }
    }
} 
