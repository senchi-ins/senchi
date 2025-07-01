//
//  BluetoothManager.swift
//  senchi
//
//  Created by Michael Dawes on 2025-06-30.
//

import Foundation
import CoreBluetooth

protocol BluetoothManagerDelegate: AnyObject {
    func bluetoothManager(_ manager: BluetoothManager, didUpdateState state: CBManagerState)
    func bluetoothManager(_ manager: BluetoothManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi: NSNumber)
    func bluetoothManager(_ manager: BluetoothManager, didConnect peripheral: CBPeripheral)
    func bluetoothManager(_ manager: BluetoothManager, didFailToConnect peripheral: CBPeripheral, error: Error?)
    func bluetoothManager(_ manager: BluetoothManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?)
    func bluetoothManager(_ manager: BluetoothManager, didReceiveData data: Data, from characteristic: CBCharacteristic, interpretation: String)
    func bluetoothManager(_ manager: BluetoothManager, didLog message: String)
}

class BluetoothManager: NSObject {
    
    // MARK: - Properties
    weak var delegate: BluetoothManagerDelegate?
    private var centralManager: CBCentralManager!
    private var connectedPeripheral: CBPeripheral?
    private var discoveredDevices: [CBPeripheral] = []
    
    // MARK: - Device Specific Constants
    private let targetDeviceName = "WoSenW"
    private let targetServiceUUID = CBUUID(string: "CBA20D00-224D-11E6-9FB8-0002A5D5C51B")
    private let notifyCharacteristicUUID = CBUUID(string: "CBA20003-224D-11E6-9FB8-0002A5D5C51B")
    private let writeCharacteristicUUID = CBUUID(string: "CBA20002-224D-11E6-9FB8-0002A5D5C51B")
    
    // MARK: - Data Storage
    private var deviceProfile: [String: Any] = [:]
    private var notificationHistory: [[String: Any]] = []
    
    // MARK: - Initialization
    override init() {
        super.init()
        setupBluetoothManager()
    }
    
    private func setupBluetoothManager() {
        centralManager = CBCentralManager(delegate: self, queue: nil)
        log("Bluetooth manager initialized")
    }
    
    // MARK: - Public Methods
    func startScanning() {
        guard centralManager.state == .poweredOn else {
            log("Bluetooth is not available")
            return
        }
        discoveredDevices.removeAll()
        // Scan for the specific service UUID
        centralManager.scanForPeripherals(withServices: [targetServiceUUID], options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
        log("Started scanning for Bluetooth devices (filtered by service UUID)...")
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
    
    // MARK: - Private Methods
    private func log(_ message: String) {
        delegate?.bluetoothManager(self, didLog: message)
    }
    
    private func discoverServices(for peripheral: CBPeripheral) {
        log("Discovering services...")
        peripheral.delegate = self
        peripheral.discoverServices(nil)
    }
    
    private func discoverCharacteristics(for service: CBService) {
        log("Discovering characteristics for service: \(service.uuid)")
        service.peripheral?.discoverCharacteristics([notifyCharacteristicUUID, writeCharacteristicUUID], for: service)
    }
    
    private func interpretData(_ data: Data, for characteristic: CBCharacteristic) -> String {
        let hexString = data.map { String(format: "%02x", $0) }.joined()
        // Add custom interpretation for your device here if needed
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
        // Fallback: If not found by service, check device name
        let isTargetDevice = peripheral.name == targetDeviceName
        if isTargetDevice || (peripheral.services?.contains(where: { $0.uuid == targetServiceUUID }) ?? false) {
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

// MARK: - CBPeripheralDelegate
extension BluetoothManager: CBPeripheralDelegate {
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
            
            // Read characteristic if possible
            if characteristic.properties.contains(.read) {
                peripheral.readValue(for: characteristic)
            }
            
            // Subscribe to notifications if possible
            if characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
                peripheral.setNotifyValue(true, for: characteristic)
                log("Subscribed to notifications for \(characteristic.uuid)")
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
        
        let interpretation = interpretData(data, for: characteristic)
        addNotification(data, characteristic: characteristic, interpretation: interpretation)
        
        log("📡 \(interpretation)")
        delegate?.bluetoothManager(self, didReceiveData: data, from: characteristic, interpretation: interpretation)
    }
    
    func peripheral(_ peripheral: CBPeripheral, didReadRSSI RSSI: NSNumber, error: Error?) {
        if let error = error {
            log("RSSI read failed: \(error.localizedDescription)")
        } else {
            log("RSSI: \(RSSI) dBm")
        }
    }
} 
