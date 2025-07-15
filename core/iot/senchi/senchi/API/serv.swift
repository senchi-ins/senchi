
import Foundation


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
        
    guard var urlComponents = URLComponents(string: "\(ApplicationConfig.apiBase)/redis/set") else {
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
    request.timeoutInterval = ApplicationConfig.timeout
    
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
func permitJoin(duration: Int = 60) async throws -> String {
    guard var urlComponents = URLComponents(string: "\(ApplicationConfig.apiBase)/zigbee/permit-join") else {
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

    guard var urlComponents = URLComponents(string: "\(ApplicationConfig.apiBase)/redis/get") else {
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
