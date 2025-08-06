//
//  auth.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-24.
//

import Foundation

struct UserInfoResponse: Codable, Equatable {
    let user_id: String
    let location_id: String?
    let device_serial: String?
    let full_name: String?
    let iat: Double?
    let exp: Double
    let created_at: String?
}

enum AuthError: Error, LocalizedError {
    case invalidURL
    case serverError(String)
    case networkError(Error)
    case keychainError(String)
    case pushNotificationDenied(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .serverError(let message):
            return message
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .keychainError(let message):
            return "Keychain error: \(message)"
        case .pushNotificationDenied(let error):
            return "Push notification permission denied: \(error.localizedDescription)"
        }
    }
}

struct LoginResponse: Codable {
    let jwt_token: String
    let user_info: UserInfoResponse
}
