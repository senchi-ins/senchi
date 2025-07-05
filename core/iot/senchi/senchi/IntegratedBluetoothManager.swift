//
//  IntegratedBluetoothManager.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-02.
//

import Foundation
import CoreBluetooth
import os

protocol IntegratedBluetoothManagerDelegate: AnyObject {
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didUpdateState state: CBManagerState)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi: NSNumber)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didConnect peripheral: CBPeripheral)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didFailToConnect peripheral: CBPeripheral, error: Error?)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didReceiveData data: Data, from characteristic: CBCharacteristic, interpretation: String)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didLog message: String)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didReceiveTransferData data: Data)
    func bluetoothManager(_ manager: IntegratedBluetoothManager, didSendTransferData data: Data)
}

class IntegratedBluetoothManager: NSObject {
    
    // MARK: - Properties
    weak var delegate: IntegratedBluetoothManagerDelegate?
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
    var mode: BluetoothMode = .both
    
    // MARK: - Initialization
    override init() {
        super.init()
        setupBluetoothManager()
    }
    
    private func setupBluetoothManager() {
        centralManager = CBCentralManager(delegate: self, queue: nil)
        peripheralManager = CBPeripheralManager(delegate: self, queue: nil, options: [CBPeripheralManagerOptionShowPowerAlertKey: true])
        log("Integrated Bluetooth manager initialized")
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
        
        centralManager.cancelPeripheralConnection(peripheral)
        connectedPeripheral = nil
        log("Disconnected from device")
    }
    
    // MARK: Peripheral Mode Methods
    func startAdvertising() {
        guard peripheralManager.state == .poweredOn else {
            log("Peripheral manager not ready")
            return
        }
        
        setupPeripheral()
        peripheralManager.startAdvertising([CBAdvertisementDataServiceUUIDsKey: [TransferService.serviceUUID]])
        log("Started advertising transfer service")
    }
    
    func stopAdvertising() {
        peripheralManager.stopAdvertising()
        log("Stopped advertising")
    }
    
    func sendData(_ data: Data) {
        dataToSend = data
        sendDataIndex = 0
        IntegratedBluetoothManager.sendingEOM = false
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
    
    // MARK: - Private Methods
    private func log(_ message: String) {
        delegate?.bluetoothManager(self, didLog: message)
    }
    
    private func discoverServices(for peripheral: CBPeripheral) {
        log("Discovering services...")
        peripheral.delegate = self
        peripheral.discoverServices([targetServiceUUID, TransferService.serviceUUID])
    }
    
    private func discoverCharacteristics(for service: CBService) {
        log("Discovering characteristics for service: \(service.uuid)")
        
        if service.uuid == TransferService.serviceUUID {
            service.peripheral?.discoverCharacteristics([TransferService.characteristicUUID], for: service)
        } else {
            service.peripheral?.discoverCharacteristics([notifyCharacteristicUUID, writeCharacteristicUUID], for: service)
        }
    }
    
    private func interpretData(_ data: Data, for characteristic: CBCharacteristic) -> String {
        let hexString = data.map { String(format: "%02x", $0) }.joined()
        return "Data: \(hexString)"
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
    private func setupPeripheral() {
        let transferCharacteristic = CBMutableCharacteristic(
            type: TransferService.characteristicUUID,
            properties: [.notify, .writeWithoutResponse],
            value: nil,
            permissions: [.readable, .writeable]
        )
        
        let transferService = CBMutableService(type: TransferService.serviceUUID, primary: true)
        transferService.characteristics = [transferCharacteristic]
        
        peripheralManager.add(transferService)
        self.transferCharacteristic = transferCharacteristic
        log("Transfer service setup complete")
    }
    
    private func sendData() {
        guard let transferCharacteristic = transferCharacteristic else {
            return
        }
        
        // First up, check if we're meant to be sending an EOM
        if IntegratedBluetoothManager.sendingEOM {
            let didSend = peripheralManager.updateValue("EOM".data(using: .utf8)!, for: transferCharacteristic, onSubscribedCentrals: nil)
            if didSend {
                IntegratedBluetoothManager.sendingEOM = false
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
                IntegratedBluetoothManager.sendingEOM = true
                let eomSent = peripheralManager.updateValue("EOM".data(using: .utf8)!, for: transferCharacteristic, onSubscribedCentrals: nil)
                
                if eomSent {
                    IntegratedBluetoothManager.sendingEOM = false
                    log("Sent: EOM")
                    delegate?.bluetoothManager(self, didSendTransferData: dataToSend)
                }
                return
            }
        }
    }
}

// MARK: - CBCentralManagerDelegate
extension IntegratedBluetoothManager: CBCentralManagerDelegate {
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
        // Check for both legacy devices and transfer service devices
        let isTargetDevice = peripheral.name == targetDeviceName
        let hasTransferService = advertisementData[CBAdvertisementDataServiceUUIDsKey] as? [CBUUID] != nil
        
        if isTargetDevice || hasTransferService {
            if !discoveredDevices.contains(where: { $0.identifier == peripheral.identifier }) {
                discoveredDevices.append(peripheral)
                log("Found device: \(peripheral.name ?? "Unknown") (\(peripheral.identifier))")
                delegate?.bluetoothManager(self, didDiscover: peripheral, advertisementData: advertisementData, rssi: RSSI)
            }
        }
    }
    
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        log("Successfully connected to \(peripheral.name ?? "device")")
        delegate?.bluetoothManager(self, didConnect: peripheral)
        discoverServices(for: peripheral)
    }
    
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        log("Failed to connect: \(error?.localizedDescription ?? "Unknown error")")
        delegate?.bluetoothManager(self, didFailToConnect: peripheral, error: error)
    }
    
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        log("Disconnected from \(peripheral.name ?? "device")")
        delegate?.bluetoothManager(self, didDisconnectPeripheral: peripheral, error: error)
    }
}

// MARK: - CBPeripheralManagerDelegate
extension IntegratedBluetoothManager: CBPeripheralManagerDelegate {
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
extension IntegratedBluetoothManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let error = error {
            log("Service discovery failed: \(error.localizedDescription)")
            return
        }
        
        guard let services = peripheral.services else { return }
        
        log("Discovered \(services.count) services")
        
        for service in services {
            log("Service: \(service.uuid)")
            discoverCharacteristics(for: service)
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        if let error = error {
            log("Characteristic discovery failed: \(error.localizedDescription)")
            return
        }
        
        guard let characteristics = service.characteristics else { return }
        
        log("Discovered \(characteristics.count) characteristics for service \(service.uuid)")
        
        for characteristic in characteristics {
            log("Characteristic: \(characteristic.uuid) - Properties: \(characteristic.properties)")
            
            // Handle transfer service characteristic
            if characteristic.uuid == TransferService.characteristicUUID {
                if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
                    peripheral.setNotifyValue(true, for: characteristic)
                    log("Subscribed to transfer service notifications")
                }
            } else {
                // Handle legacy characteristics
                if characteristic.properties.contains(.read) {
                    peripheral.readValue(for: characteristic)
                }
                
                if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
                    peripheral.setNotifyValue(true, for: characteristic)
                    log("Subscribed to notifications for \(characteristic.uuid)")
                }
            }
        }
        
        // Save device profile after discovering all characteristics
        saveDeviceProfile()
    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error {
            log("Value update failed: \(error.localizedDescription)")
            return
        }
        
        guard let data = characteristic.value else { return }
        
        // Handle transfer service data
        if characteristic.uuid == TransferService.characteristicUUID {
            let stringFromData = String(data: data, encoding: .utf8)
            log("Received transfer data: \(stringFromData ?? "unknown")")
            
            if stringFromData == "EOM" {
                // End of message received
                log("Received complete transfer data")
                delegate?.bluetoothManager(self, didReceiveTransferData: receivedData)
                receivedData.removeAll(keepingCapacity: false)
            } else {
                // Append data to received buffer
                receivedData.append(data)
            }
        } else {
            // Handle legacy data
            let interpretation = interpretData(data, for: characteristic)
            addNotification(data, characteristic: characteristic, interpretation: interpretation)
            
            log("📡 \(interpretation)")
            delegate?.bluetoothManager(self, didReceiveData: data, from: characteristic, interpretation: interpretation)
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didReadRSSI RSSI: NSNumber, error: Error?) {
        if let error = error {
            log("RSSI read failed: \(error.localizedDescription)")
        } else {
            log("RSSI: \(RSSI) dBm")
        }
    }
} 
