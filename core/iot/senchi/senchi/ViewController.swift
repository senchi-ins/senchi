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
    
    // New UI elements for transfer functionality
    @IBOutlet weak var modeSegmentControl: UISegmentedControl!
    @IBOutlet weak var advertiseButton: UIButton!
    @IBOutlet weak var sendDataButton: UIButton!
    @IBOutlet weak var dataTextField: UITextField!
    @IBOutlet weak var receivedDataLabel: UILabel!
    
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
        
        // Setup mode segment control (with nil check)
        if let modeSegmentControl = modeSegmentControl {
            modeSegmentControl.removeAllSegments()
            modeSegmentControl.insertSegment(withTitle: "Central", at: 0, animated: false)
            modeSegmentControl.insertSegment(withTitle: "Peripheral", at: 1, animated: false)
            modeSegmentControl.insertSegment(withTitle: "Both", at: 2, animated: false)
            modeSegmentControl.selectedSegmentIndex = 2 // Default to both
        }
        
        // Setup advertise button (with nil check)
        if let advertiseButton = advertiseButton {
            advertiseButton.setTitle("Start Advertising", for: .normal)
            advertiseButton.backgroundColor = .systemOrange
            advertiseButton.setTitleColor(.white, for: .normal)
            advertiseButton.layer.cornerRadius = 8
            advertiseButton.isEnabled = false
        }
        
        // Setup send data button (with nil check)
        if let sendDataButton = sendDataButton {
            sendDataButton.setTitle("Send Data", for: .normal)
            sendDataButton.backgroundColor = .systemPurple
            sendDataButton.setTitleColor(.white, for: .normal)
            sendDataButton.layer.cornerRadius = 8
            sendDataButton.isEnabled = false
        }
        
        // Setup data text field (with nil check)
        if let dataTextField = dataTextField {
            dataTextField.placeholder = "Enter data to send..."
            dataTextField.borderStyle = .roundedRect
        }
        
        // Setup received data label (with nil check)
        if let receivedDataLabel = receivedDataLabel {
            receivedDataLabel.text = "Received: None"
            receivedDataLabel.numberOfLines = 0
        }
        
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
        
        updateUIForMode()
    }
    
    private func setupTableView() {
        deviceTableView.delegate = self
        deviceTableView.dataSource = self
        deviceTableView.register(UITableViewCell.self, forCellReuseIdentifier: "DeviceCell")
    }
    
    private func setupBluetoothManager() {
        bluetoothManager.delegate = self
    }
    
    private func updateUIForMode() {
        guard let modeSegmentControl = modeSegmentControl else { return }
        
        let mode = BluetoothMode(rawValue: modeSegmentControl.selectedSegmentIndex) ?? .both
        
        switch mode {
        case .central:
            scanButton.isEnabled = true
            advertiseButton?.isEnabled = false
            sendDataButton?.isEnabled = false
        case .peripheral:
            scanButton.isEnabled = false
            advertiseButton?.isEnabled = true
            sendDataButton?.isEnabled = true
        case .both:
            scanButton.isEnabled = true
            advertiseButton?.isEnabled = true
            sendDataButton?.isEnabled = true
        }
    }
    
    // MARK: - Actions
    @IBAction func modeSegmentChanged(_ sender: UISegmentedControl) {
        updateUIForMode()
        bluetoothManager.mode = BluetoothMode(rawValue: sender.selectedSegmentIndex) ?? .both
    }
    
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
    
    @IBAction func broadScanButtonTapped(_ sender: UIButton) {
        if sender.title(for: .normal) == "Stop Broad Scan" {
            stopScan()
        } else {
            startBroadScan()
        }
    }
    
    @IBAction func targetedScanButtonTapped(_ sender: UIButton) {
        if sender.title(for: .normal) == "Stop Targeted Scan" {
            stopScan()
        } else {
            startTargetedScan()
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
    
    @IBAction func advertiseButtonTapped(_ sender: UIButton) {
        guard let advertiseButton = advertiseButton else { return }
        
        if advertiseButton.title(for: .normal) == "Stop Advertising" {
            bluetoothManager.stopAdvertising()
            advertiseButton.setTitle("Start Advertising", for: .normal)
            advertiseButton.backgroundColor = .systemOrange
        } else {
            bluetoothManager.startAdvertising()
            advertiseButton.setTitle("Stop Advertising", for: .normal)
            advertiseButton.backgroundColor = .systemRed
        }
    }
    
    @IBAction func sendDataButtonTapped(_ sender: UIButton) {
        guard let dataTextField = dataTextField else { return }
        guard let text = dataTextField.text, !text.isEmpty else {
            log("No data to send")
            return
        }
        
        guard let data = text.data(using: .utf8) else {
            log("Failed to convert text to data")
            return
        }
        
        bluetoothManager.sendData(data)
        log("Sending data: \(text)")
        dataTextField.text = ""
    }
    
    @IBAction func requestStatusButtonTapped(_ sender: UIButton) {
        bluetoothManager.requestDeviceStatus()
        log("Requested device status")
    }
    
    @IBAction func enableNotificationsButtonTapped(_ sender: UIButton) {
        bluetoothManager.enableEventNotifications()
        log("Enabled event notifications")
    }
    
    @IBAction func initiateHandshakeButtonTapped(_ sender: UIButton) {
        bluetoothManager.initiateHandshake()
        log("Initiating handshake sequence...")
    }
    
    @IBAction func requestPairingButtonTapped(_ sender: UIButton) {
        bluetoothManager.requestPairing()
        log("Requesting device pairing...")
    }
    
    @IBAction func completePairingButtonTapped(_ sender: UIButton) {
        bluetoothManager.completePairing()
        log("Completing pairing process...")
    }
    
    @IBAction func resetHandshakeButtonTapped(_ sender: UIButton) {
        bluetoothManager.resetHandshake()
        log("Reset handshake state")
    }
    
    @IBAction func pingSensorButtonTapped(_ sender: UIButton) {
        bluetoothManager.pingSensor()
        log("Pinging sensor...")
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
    
    private func startBroadScan() {
        discoveredDevices.removeAll()
        deviceTableView.reloadData()
        
        bluetoothManager.startScanning() // This now does broad scanning
        
        scanButton.setTitle("Stop Broad Scan", for: .normal)
        scanButton.backgroundColor = .systemRed
        statusLabel.text = "Broad scanning for ALL devices..."
        
        // Auto-stop scan after 30 seconds for broad scanning
        DispatchQueue.main.asyncAfter(deadline: .now() + 30) { [weak self] in
            self?.stopScan()
        }
    }
    
    private func startTargetedScan() {
        discoveredDevices.removeAll()
        deviceTableView.reloadData()
        
        bluetoothManager.startTargetedScanning()
        
        scanButton.setTitle("Stop Targeted Scan", for: .normal)
        scanButton.backgroundColor = .systemRed
        statusLabel.text = "Targeted scanning for WoSenW devices..."
        
        // Auto-stop scan after 15 seconds for targeted scanning
        DispatchQueue.main.asyncAfter(deadline: .now() + 15) { [weak self] in
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
                self?.updateUIForMode()
            case .poweredOff:
                self?.statusLabel.text = "Bluetooth Status: Powered Off"
                self?.scanButton.isEnabled = false
                self?.advertiseButton.isEnabled = false
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
    
    func bluetoothManager(_ manager: BluetoothManager, didReceiveTransferData data: Data) {
        DispatchQueue.main.async { [weak self] in
            if let string = String(data: data, encoding: .utf8) {
                self?.receivedDataLabel.text = "Received: \(string)"
            } else {
                self?.receivedDataLabel.text = "Received: \(data.count) bytes"
            }
        }
    }
    
    func bluetoothManager(_ manager: BluetoothManager, didSendTransferData data: Data) {
        DispatchQueue.main.async { [weak self] in
            if let string = String(data: data, encoding: .utf8) {
                self?.log("Successfully sent transfer data: \(string)")
            } else {
                self?.log("Successfully sent \(data.count) bytes")
            }
        }
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

