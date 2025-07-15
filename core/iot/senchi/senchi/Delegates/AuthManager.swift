//
//  AuthManager.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-14.
//

import SwiftUI
import Foundation
import Security

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = true
    @Published var currentToken: String?
    @Published var locationId: String?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let keychainService = "com.yourapp.homemonitor"
    private let tokenKey = "jwt_token"
    private let locationKey = "location_id"
    
    init() {
        loadStoredCredentials()
    }
    
    func signIn(email: String, password: String) async throws {
        isLoading = true
        errorMessage = nil
        
        defer { isLoading = false }
        
        do {
            // For now, we'll simulate a successful sign in
            // In a real implementation, you would make an API call here
            print("Signing in user: \(email)")
            
            // Simulate network delay
            try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
            
            // For demo purposes, we'll just set authenticated to true
            // In production, you would validate credentials with your server
            isAuthenticated = true
            currentToken = "demo_token_\(UUID().uuidString)"
            locationId = "demo_location_\(UUID().uuidString)"
            
            print("Sign in successful for: \(email)")
            
        } catch {
            errorMessage = error.localizedDescription
            print("Sign in failed: \(error)")
            throw error
        }
    }
    
    func createAccount(fullName: String, email: String, password: String) async throws {
        isLoading = true
        errorMessage = nil
        
        defer { isLoading = false }
        
        do {
            // For now, we'll simulate account creation
            // In a real implementation, you would make an API call here
            print("Creating account for: \(fullName) (\(email))")
            
            // Simulate network delay
            try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
            
            // For demo purposes, we'll just set authenticated to true
            // In production, you would create the account on your server
            isAuthenticated = true
            currentToken = "demo_token_\(UUID().uuidString)"
            locationId = "demo_location_\(UUID().uuidString)"
            
            print("Account created successfully for: \(email)")
            
        } catch {
            errorMessage = error.localizedDescription
            print("Account creation failed: \(error)")
            throw error
        }
    }
    
    func setupDevice(serialNumber: String) async throws {
        isLoading = true
        errorMessage = nil
        
        defer { isLoading = false }
        
        do {
            // Setup device with server
            let tokenResponse = try await performDeviceSetup(
                serialNumber: serialNumber,
                pushToken: nil as String? // Will be updated later when received
            )
            
            // Store credentials securely
            try storeCredentials(token: tokenResponse.jwtToken, locationId: tokenResponse.locationId)
            
            // Update state
            currentToken = tokenResponse.jwtToken
            locationId = tokenResponse.locationId
            isAuthenticated = true
            
            print("Device setup successful! Location: \(tokenResponse.locationId)")
            
        } catch {
            errorMessage = error.localizedDescription
            print("Device setup failed: \(error)")
            throw error
        }
    }
    
    private func performDeviceSetup(serialNumber: String, pushToken: String?) async throws -> TokenResponse {
        guard let url = URL(string: "\(ApplicationConfig.apiBase)/api/auth/setup") else {
            throw AuthError.invalidURL
        }
        
        let request = TokenSetupRequest(deviceSerial: serialNumber, pushToken: pushToken)
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            throw AuthError.serverError("Setup failed")
        }
        
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
    
    func updatePushToken(_ token: String) async {
        guard let jwtToken = currentToken else {
            print("⚠️ No JWT token available for push token update")
            return
        }
        
        do {
            try await sendPushTokenUpdate(jwtToken: jwtToken, pushToken: token)
            print("✅ Push token updated successfully")
        } catch {
            print("❌ Failed to update push token: \(error)")
        }
    }
    
    private func sendPushTokenUpdate(jwtToken: String, pushToken: String) async throws {
        guard let url = URL(string: "\(ApplicationConfig.apiBase)/api/auth/push-token") else {
            throw AuthError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(jwtToken)", forHTTPHeaderField: "Authorization")
        
        let requestBody = ["push_token": pushToken]
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (_, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            throw AuthError.serverError("Push token update failed")
        }
    }
    
    // MARK: - Token Validation
    
    func verifyToken() async -> Bool {
        guard let token = currentToken else { return false }
        
        do {
            let isValid = try await validateTokenWithServer(token)
            if !isValid {
                logout()
            }
            return isValid
        } catch {
            print("❌ Token verification failed: \(error)")
            logout()
            return false
        }
    }
    
    private func validateTokenWithServer(_ token: String) async throws -> Bool {
        guard let url = URL(string: "\(ApplicationConfig.apiBase)/api/auth/verify") else {
            throw AuthError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (_, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return false
        }
        
        return 200...299 ~= httpResponse.statusCode
    }
    
    // MARK: - Secure Storage
    
    private func storeCredentials(token: String, locationId: String) throws {
        // Store JWT token
        let tokenData = token.data(using: .utf8)!
        let tokenQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: tokenKey,
            kSecValueData as String: tokenData
        ]
        
        // Delete existing token
        SecItemDelete(tokenQuery as CFDictionary)
        
        // Add new token
        let tokenStatus = SecItemAdd(tokenQuery as CFDictionary, nil)
        guard tokenStatus == errSecSuccess else {
            throw AuthError.keychainError("Failed to store token")
        }
        
        // Store location ID
        let locationData = locationId.data(using: .utf8)!
        let locationQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: locationKey,
            kSecValueData as String: locationData
        ]
        
        SecItemDelete(locationQuery as CFDictionary)
        let locationStatus = SecItemAdd(locationQuery as CFDictionary, nil)
        guard locationStatus == errSecSuccess else {
            throw AuthError.keychainError("Failed to store location")
        }
    }
    
    private func loadStoredCredentials() {
        currentToken = loadFromKeychain(key: tokenKey)
        locationId = loadFromKeychain(key: locationKey)
        isAuthenticated = currentToken != nil && locationId != nil
    }
    
    private func loadFromKeychain(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let string = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return string
    }
    
    func logout() {
        // Clear keychain
        let tokenQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: tokenKey
        ]
        
        let locationQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: locationKey
        ]
        
        SecItemDelete(tokenQuery as CFDictionary)
        SecItemDelete(locationQuery as CFDictionary)
        
        // Clear state
        currentToken = nil
        locationId = nil
        isAuthenticated = false
    }
}
