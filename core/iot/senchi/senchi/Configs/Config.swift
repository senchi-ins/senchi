
import SwiftUI


struct ApplicationConfig {
    static let wsURL: String =  "wss://senchi-mqtt.up.railway.app/ws"
    static let apiBase: String = "https://senchi-mqtt.up.railway.app"
    static let setupURL: String = "http://10.42.0.1"
    static let setupPort: String = "80"
    static let hubName: String = "HomeGuard Hub"
    static let version: String = "0.0.1"
}

struct SenchiColors {
    static let senchiBlue = Color(red: 0.141, green: 0.051, blue: 0.749)
    static let senchiBackground = Color(.white)
    static let senchiGreen = Color(red: 0.0, green: 0.7, blue: 0.3)
    static let senchiRed = Color(red: 0.85, green: 0.1, blue: 0.2)
}
