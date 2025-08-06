
import Foundation
import SwiftUI


struct SetKeyResponse: Codable {
    let message: String
}

struct GetKeyResponse: Codable {
    let key: String
    let value: String?
}

struct PermitJoinResponse: Codable {
    let message: String
}

enum RedisAPIError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError(Error)
    case httpError(Int, String?)
    case networkError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid API URL"
        case .noData:
            return "No data received from server"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .httpError(let code, let message):
            return "HTTP Error \(code): \(message ?? "Unknown error")"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}

// Core redis functions
func setKey(prefix: String, key: String, value: String, ttl: Int = 0) async throws -> String {
    let fullKey = "\(prefix):\(key)"
        
    guard var urlComponents = URLComponents(string: "\(ApplicationConfig.zbAPIBase)/redis/set") else {
        throw RedisAPIError.invalidURL
    }
    
    urlComponents.queryItems = [
        URLQueryItem(name: "key", value: fullKey),
        URLQueryItem(name: "value", value: value)
    ]
    
    if ttl > 0 {
        urlComponents.queryItems?.append(URLQueryItem(name: "ttl", value: String(ttl)))
    }
    
    guard let url = urlComponents.url else {
        throw RedisAPIError.invalidURL
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.timeoutInterval = 10
    
    do {
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse {
            guard 200...299 ~= httpResponse.statusCode else {
                let errorMessage = String(data: data, encoding: .utf8)
                throw RedisAPIError.httpError(httpResponse.statusCode, errorMessage)
            }
        }
        let setResponse = try JSONDecoder().decode(SetKeyResponse.self, from: data)
        return setResponse.message
        
    } catch let error as RedisAPIError {
        throw error
    } catch let decodingError as DecodingError {
        throw RedisAPIError.decodingError(decodingError)
    } catch {
        throw RedisAPIError.networkError(error)
    }
}

// Permit join function
func permitJoin(authManager: AuthManager, duration: Int = 60) async throws -> String {
    // Get the current token from the AuthManager
    guard let token = await authManager.currentToken else {
        throw RedisAPIError.httpError(401, "No authentication token available")
    }
    
    // Verify the token with the main server first
    guard let verifyURL = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/auth/verify") else {
        throw RedisAPIError.invalidURL
    }
    
    var verifyRequest = URLRequest(url: verifyURL)
    verifyRequest.httpMethod = "POST"
    verifyRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    verifyRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let (verifyData, resp) = try await URLSession.shared.data(for: verifyRequest)
    
    guard let httpVerifyResponse = resp as? HTTPURLResponse else {
        throw RedisAPIError.httpError(500, "Invalid response from verification server")
    }
    
    guard 200...299 ~= httpVerifyResponse.statusCode else {
        let errorMessage = String(data: verifyData, encoding: .utf8)
        throw RedisAPIError.httpError(httpVerifyResponse.statusCode, errorMessage)
    }
    
    // Print the raw response data
    if let responseString = String(data: verifyData, encoding: .utf8) {
        print("🔍 Verify response raw data: \(responseString)")
    }
    
    // Parse the verify response to get the verified token
    let verifyResponse = try JSONDecoder().decode(TokenResponse.self, from: verifyData)
    let verifiedToken = verifyResponse.jwtToken
    
    // Print the decoded response fields
    print("🔍 Verify response fields:")
    print("  - jwt_token: \(verifyResponse.jwtToken)")
    print("  - expires_at: \(verifyResponse.expiresAt)")
    print("  - user_info.user_id: \(verifyResponse.userInfo.user_id)")
    print("  - user_info.location_id: \(verifyResponse.userInfo.location_id ?? "nil")")
    print("  - user_info.device_serial: \(verifyResponse.userInfo.device_serial ?? "nil")")
    print("  - user_info.full_name: \(verifyResponse.userInfo.full_name ?? "nil")")
    print("  - user_info.iat: \(verifyResponse.userInfo.iat ?? 0)")
    print("  - user_info.exp: \(verifyResponse.userInfo.exp)")
    print("  - user_info.created_at: \(verifyResponse.userInfo.created_at ?? "nil")")
    
    // Now call the Zigbee server with the verified token
    guard var urlComponents = URLComponents(string: "\(ApplicationConfig.zbAPIBase)/zigbee/permit-join") else {
        throw RedisAPIError.invalidURL
    }
    
    urlComponents.queryItems = [
        URLQueryItem(name: "duration", value: String(duration))
    ]
    
    guard let url = urlComponents.url else {
        throw RedisAPIError.invalidURL
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(verifiedToken)", forHTTPHeaderField: "Authorization")
    request.timeoutInterval = 10
    
    do {
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse {
            guard 200...299 ~= httpResponse.statusCode else {
                let errorMessage = String(data: data, encoding: .utf8)
                throw RedisAPIError.httpError(httpResponse.statusCode, errorMessage)
            }
        }
        
        let permitResponse = try JSONDecoder().decode(PermitJoinResponse.self, from: data)
        return permitResponse.message
        
    } catch let error as RedisAPIError {
        throw error
    } catch let decodingError as DecodingError {
        throw RedisAPIError.decodingError(decodingError)
    } catch {
        throw RedisAPIError.networkError(error)
    }
}

func getKey(prefix: String, key: String) async throws -> String  {

    let fullKey = "\(prefix):\(key)"

    guard var urlComponents = URLComponents(string: "\(ApplicationConfig.zbAPIBase)/redis/get") else {
        throw RedisAPIError.invalidURL
    }
    
    urlComponents.queryItems = [
        URLQueryItem(name: "key", value: fullKey)
    ]
    
    guard let url = urlComponents.url else {
        throw RedisAPIError.invalidURL
    }
    

    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("application/json", forHTTPHeaderField: "Accept")
    request.timeoutInterval = ApplicationConfig.timeout
    
    do {
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse {
            guard 200...299 ~= httpResponse.statusCode else {
                let errorMessage = String(data: data, encoding: .utf8)
                throw RedisAPIError.httpError(httpResponse.statusCode, errorMessage)
            }
        }
        
        let getResponse = try JSONDecoder().decode(GetKeyResponse.self, from: data)
        return getResponse.value ?? "Not found"
        
    } catch let error as RedisAPIError {
        throw error
    } catch let decodingError as DecodingError {
        throw RedisAPIError.decodingError(decodingError)
    } catch {
        throw RedisAPIError.networkError(error)
    }
}

func calculateSavings() async -> Double {
    // TODO: Implement API call to calculate savings based on:
    // - Water leak prevention
    // - Energy efficiency improvements
    // - Insurance premium reductions
    // - Maintenance cost avoidance
    
    // For now, return 0
    return 0.0
}

// MARK: - Property Management

func addProperty(userId: String, propertyName: String, authManager: AuthManager) async throws -> PropertyResponse {
    guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/property/add") else {
        throw RedisAPIError.invalidURL
    }
    
    // Get the current token from AuthManager
    guard let token = await authManager.currentToken else {
        throw RedisAPIError.httpError(401, "No authentication token available")
    }
    
    let requestBody = PropertyRequest(user_id: userId, property_name: propertyName)
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    
    do {
        request.httpBody = try JSONEncoder().encode(requestBody)
    } catch {
        throw RedisAPIError.decodingError(error)
    }
    
    do {
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw RedisAPIError.httpError(500, "Invalid response from server")
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw RedisAPIError.httpError(httpResponse.statusCode, errorMessage)
        }
        
        let propertyResponse = try JSONDecoder().decode(PropertyResponse.self, from: data)
        print("Property added successfully: \(propertyResponse.name)")
        return propertyResponse
        
    } catch let error as RedisAPIError {
        throw error
    } catch let decodingError as DecodingError {
        throw RedisAPIError.decodingError(decodingError)
    } catch {
        throw RedisAPIError.networkError(error)
    }
}

func getProperties(userId: String, authManager: AuthManager) async throws -> [PropertyResponse] {
    guard let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/property/list") else {
        throw RedisAPIError.invalidURL
    }
    
    // Get the current token from AuthManager
    guard let token = await authManager.currentToken else {
        throw RedisAPIError.httpError(401, "No authentication token available")
    }
    
    // TODO: Add sep request for get / add properties
    let requestBody = PropertyRequest(user_id: userId, property_name: "")
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    
    do {
        request.httpBody = try JSONEncoder().encode(requestBody)
    } catch {
        throw RedisAPIError.decodingError(error)
    }
    
    do {
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw RedisAPIError.httpError(500, "Invalid response from server")
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw RedisAPIError.httpError(httpResponse.statusCode, errorMessage)
        }
        
        let properties = try JSONDecoder().decode([PropertyResponse].self, from: data)
        print("Retrieved \(properties.count) properties")
        return properties
        
    } catch let error as RedisAPIError {
        throw error
    } catch let decodingError as DecodingError {
        throw RedisAPIError.decodingError(decodingError)
    } catch {
        throw RedisAPIError.networkError(error)
    }
}

// Helper function to get property names as strings (for backward compatibility)
func getPropertyNames(userId: String, authManager: AuthManager) async -> [String] {
    do {
        let properties = try await getProperties(userId: userId, authManager: authManager)
        return properties.map { $0.name }
    } catch {
        print("Failed to fetch properties: \(error)")
        // Fallback to default properties
        return ["Main"]
    }
}


