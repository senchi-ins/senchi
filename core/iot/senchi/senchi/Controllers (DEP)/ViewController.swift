//
//  ViewController.swift
//  senchi
//
//  Created by Michael Dawes on 2025-01-27.
//

import UIKit
import Network
import UserNotifications

class ViewController: UIViewController {
    
    // MARK: - UI Elements
    private var connectionStatusView: UIView!
    private var statusTitleLabel: UILabel!
    private var statusTextLabel: UILabel!
    private var apiStatusLabel: UILabel!
    private var wsStatusLabel: UILabel!
    
    private var controlsStackView: UIStackView!
    private var addDeviceButton: UIButton!
    private var testAlertButton: UIButton!
    private var clearLogsButton: UIButton!
    
    private var deviceTableView: UITableView!
    private var logsTextView: UITextView!
    
    // MARK: - Properties
    private var webSocketTask: URLSessionWebSocketTask?
    private var devices: [String: IoTDevice] = [:]
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 5
    private var reconnectTimer: Timer?
    
    // Config
    private var cfg = ApplicationConfig();
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupTableView()
        setupNotifications()
        connectWebSocket()
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        disconnectWebSocket()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        title = "🏠 Home Automation System"
        
        // Create UI elements programmatically
        createUIProgrammatically()
    }
    
    private func createUIProgrammatically() {
        view.backgroundColor = .systemBackground
        
        // Connection status view
        connectionStatusView = UIView()
        connectionStatusView.translatesAutoresizingMaskIntoConstraints = false
        connectionStatusView.layer.cornerRadius = 12
        connectionStatusView.layer.shadowColor = UIColor.black.cgColor
        connectionStatusView.layer.shadowOffset = CGSize(width: 0, height: 2)
        connectionStatusView.layer.shadowOpacity = 0.1
        connectionStatusView.layer.shadowRadius = 10
        view.addSubview(connectionStatusView)
        
        // Status labels
        statusTitleLabel = UILabel()
        statusTitleLabel.text = "🏠 Home Automation System"
        statusTitleLabel.font = UIFont.boldSystemFont(ofSize: 18)
        statusTitleLabel.translatesAutoresizingMaskIntoConstraints = false
        connectionStatusView.addSubview(statusTitleLabel)
        
        statusTextLabel = UILabel()
        statusTextLabel.text = "Connecting..."
        statusTextLabel.translatesAutoresizingMaskIntoConstraints = false
        connectionStatusView.addSubview(statusTextLabel)
        
        apiStatusLabel = UILabel()
        apiStatusLabel.text = "API: Checking..."
        apiStatusLabel.translatesAutoresizingMaskIntoConstraints = false
        connectionStatusView.addSubview(apiStatusLabel)
        
        wsStatusLabel = UILabel()
        wsStatusLabel.text = "WebSocket: Connecting..."
        wsStatusLabel.translatesAutoresizingMaskIntoConstraints = false
        connectionStatusView.addSubview(wsStatusLabel)
        
        // Controls stack view
        controlsStackView = UIStackView()
        controlsStackView.axis = .horizontal
        controlsStackView.distribution = .fillEqually
        controlsStackView.spacing = 10
        controlsStackView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(controlsStackView)
        
        // Buttons
        addDeviceButton = UIButton(type: .system)
        addDeviceButton.setTitle("Add Device", for: .normal)
        addDeviceButton.backgroundColor = .systemBlue
        addDeviceButton.setTitleColor(.white, for: .normal)
        addDeviceButton.layer.cornerRadius = 8
        addDeviceButton.addTarget(self, action: #selector(addDeviceButtonTapped), for: .touchUpInside)
        controlsStackView.addArrangedSubview(addDeviceButton)
        
        testAlertButton = UIButton(type: .system)
        testAlertButton.setTitle("Test Alert", for: .normal)
        testAlertButton.backgroundColor = .systemOrange
        testAlertButton.setTitleColor(.white, for: .normal)
        testAlertButton.layer.cornerRadius = 8
        testAlertButton.addTarget(self, action: #selector(testAlertButtonTapped), for: .touchUpInside)
        controlsStackView.addArrangedSubview(testAlertButton)
        
        clearLogsButton = UIButton(type: .system)
        clearLogsButton.setTitle("Clear Logs", for: .normal)
        clearLogsButton.backgroundColor = .systemRed
        clearLogsButton.setTitleColor(.white, for: .normal)
        clearLogsButton.layer.cornerRadius = 8
        clearLogsButton.addTarget(self, action: #selector(clearLogsButtonTapped), for: .touchUpInside)
        controlsStackView.addArrangedSubview(clearLogsButton)
        
        // Device table view
        deviceTableView = UITableView()
        deviceTableView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(deviceTableView)
        
        // Logs text view
        logsTextView = UITextView()
        logsTextView.translatesAutoresizingMaskIntoConstraints = false
        logsTextView.layer.borderColor = UIColor.systemGray.cgColor
        logsTextView.layer.borderWidth = 1
        logsTextView.layer.cornerRadius = 8
        logsTextView.font = UIFont.monospacedSystemFont(ofSize: 12, weight: .regular)
        logsTextView.backgroundColor = UIColor.systemBackground
        logsTextView.isEditable = false
        view.addSubview(logsTextView)
        
        // Setup constraints
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Connection status view
            connectionStatusView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            connectionStatusView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            connectionStatusView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Status title label
            statusTitleLabel.topAnchor.constraint(equalTo: connectionStatusView.topAnchor, constant: 16),
            statusTitleLabel.leadingAnchor.constraint(equalTo: connectionStatusView.leadingAnchor, constant: 16),
            statusTitleLabel.trailingAnchor.constraint(equalTo: connectionStatusView.trailingAnchor, constant: -16),
            
            // Status text label
            statusTextLabel.topAnchor.constraint(equalTo: statusTitleLabel.bottomAnchor, constant: 8),
            statusTextLabel.leadingAnchor.constraint(equalTo: connectionStatusView.leadingAnchor, constant: 16),
            statusTextLabel.trailingAnchor.constraint(equalTo: connectionStatusView.trailingAnchor, constant: -16),
            
            // API status label
            apiStatusLabel.topAnchor.constraint(equalTo: statusTextLabel.bottomAnchor, constant: 4),
            apiStatusLabel.leadingAnchor.constraint(equalTo: connectionStatusView.leadingAnchor, constant: 16),
            apiStatusLabel.trailingAnchor.constraint(equalTo: connectionStatusView.trailingAnchor, constant: -16),
            
            // WebSocket status label
            wsStatusLabel.topAnchor.constraint(equalTo: apiStatusLabel.bottomAnchor, constant: 4),
            wsStatusLabel.leadingAnchor.constraint(equalTo: connectionStatusView.leadingAnchor, constant: 16),
            wsStatusLabel.trailingAnchor.constraint(equalTo: connectionStatusView.trailingAnchor, constant: -16),
            wsStatusLabel.bottomAnchor.constraint(equalTo: connectionStatusView.bottomAnchor, constant: -16),
            
            // Controls stack view
            controlsStackView.topAnchor.constraint(equalTo: connectionStatusView.bottomAnchor, constant: 20),
            controlsStackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            controlsStackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            controlsStackView.heightAnchor.constraint(equalToConstant: 44),
            
            // Device table view
            deviceTableView.topAnchor.constraint(equalTo: controlsStackView.bottomAnchor, constant: 20),
            deviceTableView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            deviceTableView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            deviceTableView.heightAnchor.constraint(equalToConstant: 200),
            
            // Logs text view
            logsTextView.topAnchor.constraint(equalTo: deviceTableView.bottomAnchor, constant: 20),
            logsTextView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            logsTextView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            logsTextView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20)
        ])
    }
    
    private func setupTableView() {
        deviceTableView.delegate = self
        deviceTableView.dataSource = self
        deviceTableView.register(DeviceTableViewCell.self, forCellReuseIdentifier: "DeviceCell")
        deviceTableView.rowHeight = UITableView.automaticDimension
        deviceTableView.estimatedRowHeight = 80
    }
    
    private func setupNotifications() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if let error = error {
                self.log("Notification permission error: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - WebSocket Connection
    private func connectWebSocket() {
        let wsUrl = ApplicationConfig.wsURL;
        guard let url = URL(string: wsUrl) else {
            log("Invalid WebSocket URL")
            return
        }
        
        log("Connecting to WebSocket: \(wsUrl)")
        
        let session = URLSession(configuration: .default)
        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()
        
        receiveMessage()
        
        // Set up ping to keep connection alive
        schedulePing()
    }
    
    private func disconnectWebSocket() {
        webSocketTask?.cancel()
        webSocketTask = nil
        reconnectTimer?.invalidate()
        reconnectTimer = nil
    }
    
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                self?.handleWebSocketMessage(message)
                self?.receiveMessage() // Continue receiving
            case .failure(let error):
                self?.log("WebSocket receive error: \(error.localizedDescription)")
                self?.handleWebSocketDisconnection()
            }
        }
    }
    
    private func handleWebSocketMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            handleTextMessage(text)
        case .data(let data):
            if let text = String(data: data, encoding: .utf8) {
                handleTextMessage(text)
            }
        @unknown default:
            log("Unknown WebSocket message type")
        }
    }
    
    private func handleTextMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else {
            log("Failed to convert message to data")
            return
        }
        
        do {
            let message = try JSONDecoder().decode(WebSocketMessage.self, from: data)
            handleDecodedMessage(message)
        } catch {
            log("Failed to decode message: \(error.localizedDescription)")
        }
    }
    
    private func handleDecodedMessage(_ message: WebSocketMessage) {
        log("Received message: \(message.type)")
        
        switch message.type {
        case "device_update":
            handleDeviceUpdate(message)
        case "device_list_update":
            handleDeviceListUpdate(message)
        default:
            log("Unknown message type: \(message.type)")
        }
    }
    
    private func handleDeviceUpdate(_ message: WebSocketMessage) {
        guard let deviceId = message.deviceId,
              let data = message.data else { return }
        
        let existingDevice = devices[deviceId] ?? IoTDevice(id: deviceId)
        let updatedDevice = IoTDevice(
            id: deviceId,
            name: existingDevice.name,
            status: data,
            lastSeen: Date()
        )
        
        devices[deviceId] = updatedDevice
        
        // Check for alerts
        checkForAlerts(deviceId: deviceId, data: data)
        
        // Update UI
        DispatchQueue.main.async { [weak self] in
            self?.deviceTableView.reloadData()
        }
        
        log("Device updated: \(deviceId)")
    }
    
    private func handleDeviceListUpdate(_ message: WebSocketMessage) {
        guard let deviceList = message.devices else { return }
        
        log("Device list updated")
        
        for device in deviceList {
            devices[device.id] = device
        }
        
        DispatchQueue.main.async { [weak self] in
            self?.deviceTableView.reloadData()
        }
    }
    
    private func handleWebSocketDisconnection() {
        log("WebSocket disconnected")
        updateConnectionStatus(connected: false)
        attemptReconnect()
    }
    
    private func attemptReconnect() {
        if reconnectAttempts < maxReconnectAttempts {
            reconnectAttempts += 1
            let delay = min(pow(2.0, Double(reconnectAttempts)), 30.0)
            
            log("Reconnecting in \(Int(delay))s (attempt \(reconnectAttempts))")
            
            reconnectTimer = Timer.scheduledTimer(withTimeInterval: delay, repeats: false) { [weak self] _ in
                self?.connectWebSocket()
            }
        } else {
            log("Max reconnection attempts reached")
            showNotification(message: "Connection lost - please refresh", type: .error)
        }
    }
    
    private func schedulePing() {
        Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            self?.webSocketTask?.sendPing { error in
                if let error = error {
                    self?.log("Ping error: \(error.localizedDescription)")
                }
            }
        }
    }
    
    // MARK: - Alert Handling
    private func checkForAlerts(deviceId: String, data: DeviceStatus) {
        let device = devices[deviceId]
        let deviceName = device?.name ?? deviceId
        
        // Water leak alert
        if data.waterLeak == true {
            showNotification(message: "🚨 WATER LEAK DETECTED!\n\(deviceName)", type: .error)
            log("LEAK ALERT: \(deviceName)")
        }
        
        // Low battery alert
        if data.batteryLow == true || (data.battery != nil && data.battery! < 20) {
            let batteryLevel = data.battery != nil ? "\(data.battery!)%" : "?"
            showNotification(message: "🔋 Low battery: \(deviceName) (\(batteryLevel))", type: .warning)
            log("LOW BATTERY: \(deviceName)")
        }
        
        // Device back online
        if data.linkQuality != nil && data.linkQuality! > 0 {
            if let lastSeen = device?.lastSeen,
               Date().timeIntervalSince(lastSeen) > 3600 { // 1 hour
                showNotification(message: "📡 Device back online: \(deviceName)", type: .success)
            }
        }
    }
    
    // MARK: - UI Updates
    private func updateConnectionStatus(connected: Bool) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            if connected {
                self.connectionStatusView.backgroundColor = UIColor.systemGreen.withAlphaComponent(0.1)
                self.connectionStatusView.layer.borderColor = UIColor.systemGreen.cgColor
                self.connectionStatusView.layer.borderWidth = 2
                self.statusTextLabel.text = "System Online"
                self.wsStatusLabel.text = "WebSocket: Connected"
                self.reconnectAttempts = 0
            } else {
                self.connectionStatusView.backgroundColor = UIColor.systemRed.withAlphaComponent(0.1)
                self.connectionStatusView.layer.borderColor = UIColor.systemRed.cgColor
                self.connectionStatusView.layer.borderWidth = 2
                self.statusTextLabel.text = "System Offline"
                self.wsStatusLabel.text = "WebSocket: Disconnected"
            }
        }
    }
    
    // MARK: - Notifications
    private func showNotification(message: String, type: NotificationType) {
        // In-app notification
        let alert = UIAlertController(title: type.title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        
        DispatchQueue.main.async { [weak self] in
            self?.present(alert, animated: true)
        }
        
        // Local notification
        let content = UNMutableNotificationContent()
        content.title = type.title
        content.body = message
        content.sound = .default
        
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }
    
    enum NotificationType {
        case error, warning, success, info
        
        var title: String {
            switch self {
            case .error: return "Alert"
            case .warning: return "Warning"
            case .success: return "Success"
            case .info: return "Info"
            }
        }
    }
    
    // MARK: - Actions
    @objc private func addDeviceButtonTapped(_ sender: UIButton) {
        enablePairing()
    }
    
    @objc private func testAlertButtonTapped(_ sender: UIButton) {
        showNotification(message: "🧪 Test notification - system is working!", type: .info)
    }
    
    @objc private func clearLogsButtonTapped(_ sender: UIButton) {
        logsTextView.text = ""
    }
    
    // MARK: - API Calls
    private func enablePairing() {
        guard let url = URL(string: "\(ApplicationConfig.apiBase)/zigbee/permit-join") else {
            log("Invalid pairing URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            if let error = error {
                self?.log("Pairing failed: \(error.localizedDescription)")
                self?.showNotification(message: "Failed to enable pairing mode", type: .error)
                return
            }
            
            self?.log("Pairing mode enabled")
            self?.showNotification(message: "Pairing mode enabled - add your device now!", type: .success)
        }.resume()
    }
    
    // MARK: - Logging
    private func log(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let logMessage = "[\(timestamp)] \(message)\n"
        
        DispatchQueue.main.async { [weak self] in
            self?.logsTextView.text += logMessage
            self?.logsTextView.scrollRangeToVisible(NSRange(location: self?.logsTextView.text.count ?? 0, length: 0))
        }
    }
}

// MARK: - UITableViewDataSource & UITableViewDelegate
extension ViewController: UITableViewDataSource, UITableViewDelegate {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return devices.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "DeviceCell", for: indexPath) as! DeviceTableViewCell
        
        let deviceId = Array(devices.keys)[indexPath.row]
        let device = devices[deviceId]!
        
        cell.configure(with: device)
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return UITableView.automaticDimension
    }
}

// MARK: - Device Table View Cell
class DeviceTableViewCell: UITableViewCell {
    private let deviceNameLabel = UILabel()
    private let statusStackView = UIStackView()
    private let lastSeenLabel = UILabel()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        // Device name label
        deviceNameLabel.font = UIFont.boldSystemFont(ofSize: 16)
        deviceNameLabel.numberOfLines = 0
        
        // Status stack view
        statusStackView.axis = .horizontal
        statusStackView.distribution = .fillProportionally
        statusStackView.spacing = 8
        
        // Last seen label
        lastSeenLabel.font = UIFont.systemFont(ofSize: 12)
        lastSeenLabel.textColor = .systemGray
        
        // Layout
        let mainStackView = UIStackView(arrangedSubviews: [deviceNameLabel, statusStackView, lastSeenLabel])
        mainStackView.axis = .vertical
        mainStackView.spacing = 8
        mainStackView.translatesAutoresizingMaskIntoConstraints = false
        
        contentView.addSubview(mainStackView)
        
        NSLayoutConstraint.activate([
            mainStackView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            mainStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            mainStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            mainStackView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -12)
        ])
    }
    
    func configure(with device: IoTDevice) {
        deviceNameLabel.text = device.name ?? device.id
        
        // Clear previous status items
        statusStackView.arrangedSubviews.forEach { $0.removeFromSuperview() }
        
        let status = device.status
        
        // Water leak status
        if let waterLeak = status.waterLeak {
            let statusItem = createStatusItem(
                text: waterLeak ? "💧 LEAK DETECTED" : "✅ No Leak",
                isAlert: waterLeak
            )
            statusStackView.addArrangedSubview(statusItem)
        }
        
        // Battery status
        if let battery = status.battery {
            let isLowBattery = status.batteryLow == true || battery < 20
            let statusItem = createStatusItem(
                text: "🔋 \(battery)%",
                isWarning: isLowBattery
            )
            statusStackView.addArrangedSubview(statusItem)
        }
        
        // Signal quality
        if let linkQuality = status.linkQuality {
            let signalStrength = linkQuality > 100 ? "good" : linkQuality > 50 ? "fair" : "poor"
            let statusItem = createStatusItem(
                text: "📶 \(linkQuality) (\(signalStrength))",
                isSafe: true
            )
            statusStackView.addArrangedSubview(statusItem)
        }
        
        // Temperature
        if let temperature = status.deviceTemperature {
            let statusItem = createStatusItem(
                text: "🌡️ \(String(format: "%.1f", temperature))°C",
                isSafe: true
            )
            statusStackView.addArrangedSubview(statusItem)
        }
        
        // Last seen
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        lastSeenLabel.text = "Last seen: \(formatter.string(from: device.lastSeen))"
        
        // Background color based on alert status
        if status.waterLeak == true {
            backgroundColor = UIColor.systemRed.withAlphaComponent(0.1)
            layer.borderColor = UIColor.systemRed.cgColor
            layer.borderWidth = 1
        } else {
            backgroundColor = UIColor.systemGreen.withAlphaComponent(0.1)
            layer.borderColor = UIColor.systemGreen.cgColor
            layer.borderWidth = 1
        }
        
        layer.cornerRadius = 8
    }
    
    private func createStatusItem(text: String, isAlert: Bool = false, isWarning: Bool = false, isSafe: Bool = false) -> UIView {
        let label = UILabel()
        label.text = text
        label.font = UIFont.systemFont(ofSize: 12, weight: .medium)
        label.textAlignment = .center
        label.numberOfLines = 0
        
        let container = UIView()
        container.addSubview(label)
        label.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            label.topAnchor.constraint(equalTo: container.topAnchor, constant: 4),
            label.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 8),
            label.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -8),
            label.bottomAnchor.constraint(equalTo: container.bottomAnchor, constant: -4)
        ])
        
        container.layer.cornerRadius = 12
        
        if isAlert {
            container.backgroundColor = UIColor.systemRed.withAlphaComponent(0.2)
            label.textColor = UIColor.systemRed
        } else if isWarning {
            container.backgroundColor = UIColor.systemOrange.withAlphaComponent(0.2)
            label.textColor = UIColor.systemOrange
        } else if isSafe {
            container.backgroundColor = UIColor.systemGreen.withAlphaComponent(0.2)
            label.textColor = UIColor.systemGreen
        }
        
        return container
    }
}

