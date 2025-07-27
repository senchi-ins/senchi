
import SwiftUI


struct ApplicationConfig {
    // Websocket which monitors MQTT service
    static let wsURL: String =  "wss://senchi-mqtt.up.railway.app"
    // static let wsURL: String =  "ws://192.168.2.57:8080"
    
    // API for ONLY zigbee related services
    static let zbAPIBase: String = "https://senchi-mqtt.up.railway.app"
    
    // Main API which includes auth, etc.
    static let restAPIBase: String = "https://api.senchi.ca"
    
    // IP address for development
    // static let restAPIBase: String = "http://192.168.2.57:8000"
    
    // General config
    static let timeout: TimeInterval = 10
    static let hubName: String = "HomeGuard Hub"
    static let version: String = "0.0.2"
    
    // Raspberry pi config settings
    // TODO: Confirm this URL is consistent across Pis
    static let setupURL: String = "http://10.42.0.1"
    static let setupPort: String = "80"
}

struct SenchiColors {
    static let senchiBlue = Color(red: 0.141, green: 0.051, blue: 0.749)
    static let senchiBackground = Color(.white)
    static let senchiGreen = Color(red: 0.0, green: 0.7, blue: 0.3)
    static let senchiRed = Color(red: 0.85, green: 0.1, blue: 0.2)
    static let senchiBlack = Color.black
    static let senchiGrey = Color.gray
}
