
import Foundation
import Network
import Combine
import SwiftUI
import Security

struct DeviceUpdatePayload: Codable {
    let battery_low: Bool?
    let linkquality: Int?
    let water_leak: Bool?
    let battery: Int?
    let device_temperature: Double?
    let voltage: Int?
    let power_outage_count: Int?
    let trigger_count: Int?
}

class WebSocketManager: ObservableObject {
    @Published var devices: [Device] = []
    @Published var deviceCount: Int = 0
    @Published var isConnected: Bool = false
    
    private var webSocket: URLSessionWebSocketTask?
    private var timer: Timer?
    private var userId: String
    private var selectedProperty: String = "main"
    private var heartbeatTimer: Timer?
    
    init(userId: String) {
        self.userId = userId
    }
    
    deinit {
        disconnect()
    }
    
    func updateUserId(_ newUserId: String) {
        // Disconnect current connection
        disconnect()
        
        // Update userId and reconnect
        userId = newUserId
        setupWebSocket()
    }
    
    func updateProperty(_ newProperty: String) {
        selectedProperty = newProperty
        fetchDevices()
    }
    
    func setupWebSocket() {
        // Get the JWT token from keychain
        let token = loadTokenFromKeychain()
        
        guard let token = token else {

            return
        }
        
        let wsUrlString = "\(ApplicationConfig.wsURL)/ws/\(userId)"
        print("🔍 Constructing WebSocket URL: \(wsUrlString)")
        
        guard let url = URL(string: wsUrlString) else {

            return
        }
    
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        
        print("Resuming WebSocket connection...")
        webSocket?.resume()
        
        DispatchQueue.main.async {
            print("Setting initial connection status to true")
            self.isConnected = true
        }
        
        print("Starting message reception...")
        receiveMessage()
        
        print("Setting up heartbeat timer...")
        timer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            self?.sendHeartbeat()
        }
        
        fetchDevices()
    }
    
    func connect() {
        webSocket?.resume()
        receiveMessage()
    }
    
    func disconnect() {
        webSocket?.cancel()
        timer?.invalidate()
        timer = nil
        isConnected = false
    }
    
    func reconnect() {
        print("Attempting to reconnect to WebSocket...")
        disconnect()
        
        // Small delay to ensure disconnect is complete
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            self.setupWebSocket()
            // Fetch devices after reconnection
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                self.fetchDevices()
            }
        }
    }
    
    func fetchDevices() {
        guard let url = URL(string: ApplicationConfig.zbAPIBase + "/devices") else {
            print("Invalid devices API URL")
            return
        }
        
        // Create DeviceRequest body with property_id support
        var requestBody: [String: Any] = [
            "user_id": userId,
            "property_name": selectedProperty
        ]
        
        // Add property_id if available (for future use)
        // requestBody["property_id"] = propertyId // TODO: Add when property support is implemented
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            print("Failed to serialize request body: \(error)")
            return
        }
        
        let task = URLSession.shared.dataTask(with: urlRequest) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("Failed to fetch devices: \(error)")
                    return
                }
                
                guard let data = data else {
                    print("No data received from devices API")
                    return
                }
                
                do {
                    let devices = try JSONDecoder().decode([Device].self, from: data)
                    self?.devices = devices
                    self?.deviceCount = devices.count
                    print("Fetched \(devices.count) devices from API")
                } catch {
                    print("Failed to parse devices response: \(error)")
                }
            }
        }
        task.resume()
    }
    
    private func receiveMessage() {
        print("Setting up message receiver...")
        webSocket?.receive { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let message):
                    print("WebSocket message received successfully")
                    self?.handleMessage(message)

                    if !(self?.isConnected ?? false) {
                        print("Setting connection status to true after message")
                        self?.isConnected = true
                    }

                    self?.receiveMessage()
                case .failure(let error):
                    print("WebSocket receive error: \(error)")
                    self?.isConnected = false
                    // Attempt to reconnect after a delay
                    DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
                        print("Attempting automatic reconnection...")
                        self?.setupWebSocket()
                    }
                }
            }
        }
    }
    
    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            // print("Received text message: \(text)")
            handleTextMessage(text)
        case .data(let data):
            // print("Received data message: \(data)")
            if let text = String(data: data, encoding: .utf8) {
                handleTextMessage(text)
            }
        @unknown default:
            print("Unknown message type")
        }
    }
    
    private func handleTextMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else {
            print("Failed to convert message to data")
            return
        }
        
        do {
            let message = try JSONDecoder().decode(WebSocketMessage.self, from: data)
            // print("Decoded message: \(message)")
            
            switch message.type {
            case "device_update":
                if let deviceId = message.deviceId, let payload = message.data {
                    updateDevice(deviceId: deviceId, payload: payload)
                }
            case "connection_established":
                print("WebSocket connection established with server")
                DispatchQueue.main.async {
                    self.isConnected = true
                }
            case "heartbeat_response":
                print("Heartbeat response received")
                DispatchQueue.main.async {
                    self.isConnected = true
                }
            case "heartbeat":
                print("Received heartbeat")
            default:
                print("Unknown message type: \(message.type)")
            }
        } catch {
            // print("Failed to decode WebSocket message: \(error)")
            // print("Raw message: \(text)")
        }
    }
    
    private func updateDevice(deviceId: String, payload: DeviceUpdatePayload) {
        // print("Updating device \(deviceId) with payload: \(payload)")
        
        // Find the device in our array and update it
        if let index = devices.firstIndex(where: { $0.id == deviceId }) {
            let existingDevice = devices[index]
            
            // Create a new device with updated properties
            let updatedDevice = Device(
                id: existingDevice.id,
                ieee_address: existingDevice.ieee_address,
                name: existingDevice.name,
                friendly_name: existingDevice.friendly_name,
                type: existingDevice.type,
                manufacturer: existingDevice.manufacturer,
                model_id: existingDevice.model_id,
                power_source: existingDevice.power_source,
                interview_completed: existingDevice.interview_completed,
                supported: existingDevice.supported,
                disabled: existingDevice.disabled,
                definition: existingDevice.definition,
                water_leak: payload.water_leak ?? existingDevice.water_leak,
                battery: payload.battery ?? existingDevice.battery,
                battery_low: payload.battery_low ?? existingDevice.battery_low,
                linkquality: payload.linkquality ?? existingDevice.linkquality,
                device_temperature: payload.device_temperature ?? existingDevice.device_temperature,
                voltage: payload.voltage ?? existingDevice.voltage,
                power_outage_count: payload.power_outage_count ?? existingDevice.power_outage_count,
                trigger_count: payload.trigger_count ?? existingDevice.trigger_count,
                last_seen: existingDevice.last_seen
            )
            
            devices[index] = updatedDevice
            print("Updated device \(deviceId) successfully")
            
            // Trigger UI update
            objectWillChange.send()
        } else {
            print("Device \(deviceId) not found in current devices list")
        }
    }
    
    private func sendHeartbeat() {
        let heartbeat = ["type": "heartbeat"]
        if let data = try? JSONSerialization.data(withJSONObject: heartbeat),
           let text = String(data: data, encoding: .utf8) {
            webSocket?.send(.string(text)) { error in
                if let error = error {
                    print("Failed to send heartbeat: \(error)")
                    DispatchQueue.main.async {
                        self.isConnected = false
                    }
                } else {
                    // If heartbeat succeeds, ensure we're marked as connected
                    DispatchQueue.main.async {
                        if !self.isConnected {
                            self.isConnected = true
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Keychain Access
    
    private func loadTokenFromKeychain() -> String? {
        let keychainService = "com.yourapp.homemonitor"
        let tokenKey = "jwt_token"
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: tokenKey,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return token
    }
}

