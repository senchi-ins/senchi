
import Foundation
import UserNotifications
import SwiftUI

struct TokenSetupRequest: Codable {
    let deviceSerial: String
    let pushToken: String?
    let email: String?
    let fullName: String?
    
    enum CodingKeys: String, CodingKey {
        case deviceSerial = "device_serial"
        case pushToken = "push_token"
        case email = "email"
        case fullName = "full_name"
    }
}

struct TokenResponse: Codable {
    let jwtToken: String
    let expiresAt: String
    let userInfo: UserInfoResponse
    
    enum CodingKeys: String, CodingKey {
        case jwtToken = "jwt_token"
        case expiresAt = "expires_at"
        case userInfo = "user_info"
    }
}

struct PushTokenUpdate: Codable {
    let pushToken: String
    
    enum CodingKeys: String, CodingKey {
        case pushToken = "push_token"
    }
}

extension Notification.Name {
    static let showLeakAlert = Notification.Name("showLeakAlert")
    static let showDeviceUpdate = Notification.Name("showDeviceUpdate")
}
