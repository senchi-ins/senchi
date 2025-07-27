import Foundation

func configureWiFi(ssid: String, password: String, completion: @escaping (Result<Data, Error>) -> Void) {
    
    // Once connected to the hotspot, the app will be able to hit the internal url
    let urlString = "\(ApplicationConfig.setupURL):\(ApplicationConfig.setupPort)/api/configure"
    guard let url = URL(string: urlString) else {
        completion(.failure(NSError(domain: "Invalid URL", code: 0, userInfo: nil)))
        return
    }
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    let body: [String: Any] = [
        "wifi": [
            "ssid": ssid,
            "password": password
        ]
    ]
    do {
        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
    } catch {
        completion(.failure(error))
        return
    }
    let task = URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion(.failure(error))
        } else if let data = data {
            completion(.success(data))
        } else {
            completion(.failure(NSError(domain: "No data", code: 0, userInfo: nil)))
        }
    }
    task.resume()
}


