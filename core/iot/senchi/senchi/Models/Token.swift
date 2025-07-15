
import Foundation
import UserNotifications
import SwiftUI

struct TokenSetupRequest: Codable {
    let deviceSerial: String
    let pushToken: String?
    
    enum CodingKeys: String, CodingKey {
        case deviceSerial = "device_serial"
        case pushToken = "push_token"
    }
}

struct TokenResponse: Codable {
    let jwtToken: String
    let expiresAt: String
    let locationId: String
    
    enum CodingKeys: String, CodingKey {
        case jwtToken = "jwt_token"
        case expiresAt = "expires_at"
        case locationId = "location_id"
    }
}

struct PushTokenUpdate: Codable {
    let pushToken: String
    
    enum CodingKeys: String, CodingKey {
        case pushToken = "push_token"
    }
}

enum AuthError: Error, LocalizedError {
    case invalidURL
    case serverError(String)
    case keychainError(String)
    case pushNotificationDenied
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid server URL"
        case .serverError(let message):
            return "Server error: \(message)"
        case .keychainError(let message):
            return "Security error: \(message)"
        case .pushNotificationDenied:
            return "Push notifications are required for leak alerts"
        }
    }
}

extension Notification.Name {
    static let showLeakAlert = Notification.Name("showLeakAlert")
    static let showDeviceUpdate = Notification.Name("showDeviceUpdate")
}
