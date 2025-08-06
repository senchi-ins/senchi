    
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
    
    func setupDevice(
        serialNumber: String,
        email: String,
        fullName: String,
        password: String,
    ) async throws {
        isLoading = true
        errorMessage = nil
        
        defer { isLoading = false }
        
        do {
            let tokenResponse = try await performDeviceSetup(
                serialNumber: serialNumber,
                pushToken: nil as String? ?? "", // TODO: Update this to use redis or similar
                email: email,
                fullName: fullName,
                password: password
            )
            try storeCredentials(token: tokenResponse.jwtToken, locationId: tokenResponse.userInfo.location_id ?? "")
            currentToken = tokenResponse.jwtToken
            locationId = tokenResponse.userInfo.location_id
            isAuthenticated = true
            
        } catch {
            errorMessage = error.localizedDescription
            throw error
        }
    }
    
    func refreshToken() async throws {
        guard let currentToken = self.currentToken else {
            throw AuthError.keychainError("No token to refresh!")
        }

        // Decode JWT to check expiration
        // TODO: This isn't actually decoding the token, fix
        let segments = currentToken.split(separator: ".")
        guard segments.count == 3,
              let payloadData = Data(base64Encoded: String(segments[1]).base64URLToBase64()),
              let payload = try? JSONSerialization.jsonObject(with: payloadData) as? [String: Any],
              let exp = payload["exp"] as? Double else {
            throw AuthError.keychainError("Invalid JWT format")
        }

        let expirationDate = Date(timeIntervalSince1970: exp)
        let now = Date()

        if expirationDate > now {
            return
        }

        guard let email = UserDefaults.standard.string(forKey: "user_email"),
              let password = UserDefaults.standard.string(forKey: "user_password") else {
            throw AuthError.keychainError("No credentials available to refresh token")
        }

        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        // NOTE: Central server
        guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/auth/login") else {
            throw AuthError.invalidURL
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body = ["email": email, "password": password]
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("Failed to refresh token: \(errorMessage)")
            throw AuthError.serverError("Token refresh failed: \(errorMessage)")
        }

        // Parse the response and update the token
        let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
        self.currentToken = loginResponse.jwt_token
        self.locationId = loginResponse.user_info.location_id
        self.isAuthenticated = true
        try storeCredentials(token: loginResponse.jwt_token, locationId: loginResponse.user_info.location_id ?? "")
        print("Token refreshed successfully from server")
    }
    
    func loginWithEmail(email: String, password: String) async throws -> UserInfoResponse? {
        isLoading = true
        errorMessage = nil
        
        defer { isLoading = false }
        
        do {
            let result = try await retrieveTokenByEmail(email: email, password: password)
            
            guard let result = result else {
                throw AuthError.serverError("No account found for this email")
            }
            
            let token = result.jwt_token
            let userInfo = result.userInfo
            
            let isValid = try await validateTokenWithServer(token)
            
            if isValid {
                try storeCredentials(token: token, locationId: userInfo.location_id ?? "")
                
                currentToken = token
                locationId = userInfo.location_id
                isAuthenticated = true
                
                if let fullName = userInfo.full_name {
                    UserDefaults.standard.set(fullName, forKey: "user_full_name")
                }
                return userInfo
            } else {
                try await refreshToken()
                return nil
            }
            
        } catch {
            errorMessage = error.localizedDescription
            print("Login failed: \(error)")
            throw error
        }
    }
    
    // TODO: Update the apiBase to zigbeeAPIBase to clarify which server its running on
    // NOTE: some JWTs will have the device serial in the payload (initial setup) while later it will not
    private func performDeviceSetup(
        serialNumber: String,
        pushToken: String,
        email: String,
        fullName: String,
        password: String
    ) async throws -> TokenResponse {
        // NOTE: This hits the central server
        guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/auth/register") else {
            throw AuthError.invalidURL
        }
        let request = TokenSetupRequest(deviceSerial: serialNumber, password: password, email: email, fullName: fullName, pushToken: pushToken)
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            throw AuthError.serverError("Setup failed with status: \(response)")
        }
        
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
    
    func updatePushToken(_ token: String) async {
        guard let url = URL(string: "\(ApplicationConfig.zbAPIBase)/api/register-device") else {
            print("❌ Invalid API URL")
            return
        }
        
        guard let authToken = self.currentToken else {
            print("❌ No auth token available")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        
        let deviceIdentifier = "ZBPhone-\(UUID().uuidString)" // TODO: Update to be more device specific
        
        let deviceInfo = [
            "model": UIDevice.current.model,
            "system_version": UIDevice.current.systemVersion,
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown",
            "vendor_id": UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
        ]
        
        let payload = [
            "device_token": token,
            "platform": "ios",
            "device_identifier": deviceIdentifier,
            "device_info": deviceInfo
        ] as [String: Any]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            let (data, response) = try await URLSession.shared.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                if httpResponse.statusCode == 200 {
                    print("✅ Device token registered successfully")
                    print("🔑 Device ID: \(deviceIdentifier)")
                    print("📱 Token: \(token.prefix(16))...")
                } else {
                    print("❌ Failed to register device token: \(httpResponse.statusCode)")
                    if let responseData = String(data: data, encoding: .utf8) {
                        print("   Response: \(responseData)")
                    }
                }
            }
        } catch {
            print("❌ Error registering device token: \(error)")
        }
    }
    
    // TODO: Verify if this should be on main server or zigbee partition
    private func sendPushTokenUpdate(jwtToken: String, pushToken: String) async throws {
        guard let url = URL(string: "\(ApplicationConfig.zbAPIBase)/api/auth/push-token") else {
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
        print("🔍 verifyToken called. Current token: \(String(describing: currentToken))")
        guard let token = currentToken else {
            return false
        }
        do {
            let isValid = try await validateTokenWithServer(token)
            if !isValid {
                logout()
            }
            return isValid
        } catch {
            logout()
            return false
        }
    }
    
    private func validateTokenWithServer(_ token: String) async throws -> Bool {
        // NOTE: This uses the central server
        guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/auth/verify") else {
            throw AuthError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (_, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return false
        }
        
        return 200...299 ~= httpResponse.statusCode
    }
    
    private func retrieveTokenByEmail(email: String, password: String) async throws -> (jwt_token: String, userInfo: UserInfoResponse)? {
        // Use server endpoint to retrieve token by email
        guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/auth/login") else {
            throw AuthError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = ["email": email, "password": password]
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw AuthError.serverError("Login failed: \(errorMessage)")
        }
        
        // Debug: Print the response data
        let responseString = String(data: data, encoding: .utf8) ?? "No data"
        print("🔍 Login response: \(responseString)")
        
        do {
            let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
            print("✅ Login response decoded successfully")
            return (jwt_token: loginResponse.jwt_token, userInfo: loginResponse.user_info)
        } catch let decodingError as DecodingError {
            print("❌ Decoding error: \(decodingError)")
            switch decodingError {
            case .keyNotFound(let key, let context):
                print("❌ Missing key: \(key.stringValue) at path: \(context.codingPath)")
            case .typeMismatch(let type, let context):
                print("❌ Type mismatch: expected \(type) at path: \(context.codingPath)")
            case .valueNotFound(let type, let context):
                print("❌ Value not found: expected \(type) at path: \(context.codingPath)")
            case .dataCorrupted(let context):
                print("❌ Data corrupted: \(context)")
            @unknown default:
                print("❌ Unknown decoding error")
            }
            print("❌ Response data: \(responseString)")
            throw AuthError.serverError("Failed to decode login response: \(decodingError.localizedDescription)")
        } catch {
            print("❌ Other error: \(error)")
            print("❌ Response data: \(responseString)")
            throw AuthError.serverError("Failed to decode login response: \(error.localizedDescription)")
        }
    }
    
    // TODO: Delete this, don't store JWT at all
    private func storeEmailTokenMapping(email: String, token: String) async throws {
        do {
            try await setKey(prefix: "email", key: email, value: token, ttl: 60 * 60 * 24 * 30) // 30 days
            print("Stored email -> token mapping for: \(email)")
        } catch {
            print("Error storing email -> token mapping: \(error)")
            // Don't throw here as this is not critical for device setup
        }
    }
    
    // TODO: Delete this, get user info from db
    // This endpoint should hit the main server
    private func getUserInfoFromToken(_ token: String) async throws -> (locationId: String, deviceSerial: String) {
        guard let url = URL(string: "\(ApplicationConfig.zbAPIBase)/api/auth/verify") else {
            throw AuthError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            throw AuthError.serverError("Failed to get user info")
        }
        
        // Debug: Print the verify response
        let responseString = String(data: data, encoding: .utf8) ?? "No data"
        
        // TODO: Move structs out of functions
        struct VerifyResponse: Codable {
            let valid: Bool
            let user_id: String
            let location_id: String
            let device_serial: String
            let expires_at: Double
        }
        
        let verifyResponse = try JSONDecoder().decode(VerifyResponse.self, from: data)
        return (locationId: verifyResponse.location_id, deviceSerial: verifyResponse.device_serial)
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
        
        currentToken = nil
        locationId = nil
        isAuthenticated = false
    }
    
    func deleteAccount() async throws {
        guard let token = currentToken else {
            throw AuthError.keychainError("Token not found")
        }
        guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/auth/delete") else {
            throw AuthError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw AuthError.serverError("Delete account failed: \(errorMessage)")
        }
        
        // Parse the response to confirm success
        do {
            let deleteResponse = try JSONDecoder().decode(DeleteResponse.self, from: data)
            print(deleteResponse)
        } catch {
            print("Failed to decode delete response: \(error)")
        }
    }
}
