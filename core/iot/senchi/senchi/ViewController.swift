//
//  ViewController.swift
//  senchi
//
//  Created by Michael Dawes on 2025-06-30.
//

import UIKit
import CoreBluetooth

class ViewController: UIViewController {
    
    // MARK: - UI Elements
    @IBOutlet weak var statusLabel: UILabel!
    @IBOutlet weak var scanButton: UIButton!
    @IBOutlet weak var connectButton: UIButton!
    @IBOutlet weak var deviceTableView: UITableView!
    @IBOutlet weak var logTextView: UITextView!
    
    // MARK: - Bluetooth Manager
    private let bluetoothManager = BluetoothManager()
    private var discoveredDevices: [CBPeripheral] = []
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupBluetoothManager()
        setupTableView()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        statusLabel.text = "Bluetooth Status: Unknown"
        scanButton.setTitle("Start Scan", for: .normal)
        connectButton.setTitle("Connect", for: .normal)
        connectButton.isEnabled = false
        
        // Style buttons
        scanButton.backgroundColor = .systemBlue
        scanButton.setTitleColor(.white, for: .normal)
        scanButton.layer.cornerRadius = 8
        
        connectButton.backgroundColor = .systemGreen
        connectButton.setTitleColor(.white, for: .normal)
        connectButton.layer.cornerRadius = 8
        
        // Style log text view
        logTextView.layer.borderColor = UIColor.systemGray.cgColor
        logTextView.layer.borderWidth = 1
        logTextView.layer.cornerRadius = 8
        logTextView.font = UIFont.monospacedSystemFont(ofSize: 12, weight: .regular)
    }
    
    private func setupTableView() {
        deviceTableView.delegate = self
        deviceTableView.dataSource = self
        deviceTableView.register(UITableViewCell.self, forCellReuseIdentifier: "DeviceCell")
    }
    
    private func setupBluetoothManager() {
        bluetoothManager.delegate = self
    }
    
    // MARK: - Actions
    @IBAction func scanButtonTapped(_ sender: UIButton) {
        if bluetoothManager.isConnected() {
            bluetoothManager.disconnect()
            updateUIForDisconnection()
        } else if scanButton.title(for: .normal) == "Stop Scan" {
            stopScan()
        } else {
            startScan()
        }
    }
    
    @IBAction func connectButtonTapped(_ sender: UIButton) {
        guard let selectedIndex = deviceTableView.indexPathForSelectedRow else {
            log("No device selected")
            return
        }
        
        let peripheral = discoveredDevices[selectedIndex.row]
        bluetoothManager.connect(to: peripheral)
    }
    
    // MARK: - Bluetooth Operations
    private func startScan() {
        discoveredDevices.removeAll()
        deviceTableView.reloadData()
        
        bluetoothManager.startScanning()
        
        scanButton.setTitle("Stop Scan", for: .normal)
        scanButton.backgroundColor = .systemRed
        statusLabel.text = "Scanning for devices..."
        
        // Auto-stop scan after 20 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) { [weak self] in
            self?.stopScan()
        }
    }
    
    private func stopScan() {
        bluetoothManager.stopScanning()
        discoveredDevices = bluetoothManager.getDiscoveredDevices()
        deviceTableView.reloadData()
        
        scanButton.setTitle("Start Scan", for: .normal)
        scanButton.backgroundColor = .systemBlue
        statusLabel.text = "Scan complete. Found \(discoveredDevices.count) devices"
    }
    
    private func updateUIForConnection() {
        scanButton.setTitle("Disconnect", for: .normal)
        scanButton.backgroundColor = .systemRed
        connectButton.isEnabled = false
    }
    
    private func updateUIForDisconnection() {
        scanButton.setTitle("Start Scan", for: .normal)
        scanButton.backgroundColor = .systemBlue
        connectButton.setTitle("Connect", for: .normal)
        connectButton.backgroundColor = .systemGreen
        connectButton.isEnabled = false
        statusLabel.text = "Disconnected"
    }
    
    // MARK: - Logging
    private func log(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let logMessage = "[\(timestamp)] \(message)\n"
        
        DispatchQueue.main.async { [weak self] in
            self?.logTextView.text += logMessage
            self?.logTextView.scrollRangeToVisible(NSRange(location: self?.logTextView.text.count ?? 0, length: 0))
        }
    }
}

// MARK: - BluetoothManagerDelegate
extension ViewController: BluetoothManagerDelegate {
    func bluetoothManager(_ manager: BluetoothManager, didUpdateState state: CBManagerState) {
        DispatchQueue.main.async { [weak self] in
            switch state {
            case .poweredOn:
                self?.statusLabel.text = "Bluetooth Status: Powered On"
                self?.scanButton.isEnabled = true
            case .poweredOff:
                self?.statusLabel.text = "Bluetooth Status: Powered Off"
                self?.scanButton.isEnabled = false
            case .unauthorized:
                self?.statusLabel.text = "Bluetooth Status: Unauthorized"
            case .unsupported:
                self?.statusLabel.text = "Bluetooth Status: Unsupported"
            case .resetting:
                self?.statusLabel.text = "Bluetooth Status: Resetting"
            case .unknown:
                self?.statusLabel.text = "Bluetooth Status: Unknown"
            @unknown default:
                self?.statusLabel.text = "Bluetooth Status: Unknown"
            }
        }
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi: NSNumber) {
        DispatchQueue.main.async { [weak self] in
            self?.discoveredDevices = manager.getDiscoveredDevices()
            self?.deviceTableView.reloadData()
        }
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didConnect peripheral: CBPeripheral) {
        DispatchQueue.main.async { [weak self] in
            self?.statusLabel.text = "Connected to \(peripheral.name ?? "device")"
            self?.updateUIForConnection()
        }
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        DispatchQueue.main.async { [weak self] in
            self?.statusLabel.text = "Connection failed"
        }
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        DispatchQueue.main.async { [weak self] in
            self?.updateUIForDisconnection()
        }
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didReceiveData data: Data, from characteristic: CBCharacteristic, interpretation: String) {
        // Data is already logged by the BluetoothManager
        // Additional UI updates can be added here if needed
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didLog message: String) {
        log(message)
    }
}

// MARK: - UITableViewDataSource & UITableViewDelegate
extension ViewController: UITableViewDataSource, UITableViewDelegate {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return discoveredDevices.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "DeviceCell", for: indexPath)
        let device = discoveredDevices[indexPath.row]
        
        cell.textLabel?.text = device.name ?? "Unknown Device"
        cell.detailTextLabel?.text = device.identifier.uuidString
        
        // Highlight target device (based on MAC address from Python script)
        let targetMACAddress = "ECD25189-92D0-6712-8C02-86B4D17BA636"
        if device.identifier.uuidString.lowercased() == targetMACAddress.lowercased() {
            cell.backgroundColor = UIColor.systemGreen.withAlphaComponent(0.2)
            cell.textLabel?.text = "🎯 \(device.name ?? "Target Device")"
        }
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        connectButton.isEnabled = true
        log("Selected device: \(discoveredDevices[indexPath.row].name ?? "Unknown")")
    }
}

