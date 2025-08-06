import SwiftUI
import Foundation
import NetworkExtension
import SystemConfiguration.CaptiveNetwork


struct WiFiQRHandler {
    static var isConnecting = false
    
    
    static func parseWiFiQR(_ qrString: String) -> (ssid: String, password: String)? {
        // Parse WIFI:T:WPA;S:NetworkName;P:Password;;
        // The device serial number which will be used for subscribing to the zigbee topics
        // is passed as the password
        guard qrString.hasPrefix("WIFI:") else { return nil }
        
        let components = qrString.components(separatedBy: ";")
        var ssid: String?
        var password: String?
        
        for component in components {
            if component.hasPrefix("S:") {
                ssid = String(component.dropFirst(2))
            } else if component.hasPrefix("P:") {
                password = String(component.dropFirst(2))
            }
        }
        
        guard let networkSSID = ssid, let networkPassword = password else {
            return nil
        }
        
        return (ssid: networkSSID, password: networkPassword)
    }
    
    static func connectToWiFi(ssid: String, password: String, completion: @escaping (Bool) -> Void) {
        guard !isConnecting else {
            print("🔍 Connection already in progress, skipping...")
            completion(false)
            return
        }
        
        isConnecting = true
        let discoveryDelay: TimeInterval = 3.0
        let reconnectDelay: TimeInterval = 10.0
        let cleanSSID = ssid.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanPassword = password.trimmingCharacters(in: .whitespacesAndNewlines)
        
        print("🔍 Starting hotspot connection process...")
        print("🔍 SSID: '\(cleanSSID)' (length: \(cleanSSID.count))")
        print("🔍 Password: '\(cleanPassword)' (length: \(cleanPassword.count))")
        
        // Remove any existing configuration first
        NEHotspotConfigurationManager.shared.removeConfiguration(forSSID: cleanSSID)
        print("🔍 Removed existing configuration for \(cleanSSID)")
        
        // Wait for network discovery (hotspots need more time to be discovered)
        DispatchQueue.main.asyncAfter(deadline: .now() + discoveryDelay) {
            print("🔍 Attempting connection after discovery delay...")
            
            let hotspotConfig = NEHotspotConfiguration(ssid: cleanSSID, passphrase: cleanPassword, isWEP: false)
            hotspotConfig.joinOnce = true
            
            NEHotspotConfigurationManager.shared.apply(hotspotConfig) { error in
                DispatchQueue.main.async {
                    if let error = error {
                        let nsError = error as NSError
                        print("❌ First connection attempt failed:")
                        print("❌ Error: \(error.localizedDescription)")
                        print("❌ Code: \(nsError.code)")
                        
                        // For hotspots, try once more after additional delay
                        DispatchQueue.main.asyncAfter(deadline: .now() + reconnectDelay) {
                            print("🔍 Retrying hotspot connection...")
                            
                            NEHotspotConfigurationManager.shared.apply(hotspotConfig) { retryError in
                                DispatchQueue.main.async {
                                    if let retryError = retryError {
                                        let retryNSError = retryError as NSError
                                        print("❌ Retry connection failed:")
                                        print("❌ Error: \(retryError.localizedDescription)")
                                        print("❌ Code: \(retryNSError.code)")
                                        isConnecting = false
                                        completion(false)
                                    } else {
                                        print("✅ Configuration applied on retry, verifying hotspot connection...")
                                        
                                        // Verify actual connection after hotspot stabilization
                                        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
                                            let currentSSID = getCurrentWiFiSSID()
                                            let actuallyConnected = currentSSID == cleanSSID
                                            
                                            print("🔍 Current SSID after retry: '\(currentSSID ?? "none")'")
                                            print("🔍 Expected SSID: '\(cleanSSID)'")
                                            print("🔍 Actually connected: \(actuallyConnected)")
                                            
                                            isConnecting = false
                                            completion(actuallyConnected)
                                        }
                                    }
                                }
                            }
                        }
                    } else {
                        print("✅ Configuration applied successfully, verifying hotspot connection...")
                        
                        // Verify actual connection (important for hotspots)
                        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
                            let currentSSID = getCurrentWiFiSSID()
                            let actuallyConnected = currentSSID == cleanSSID
                            
                            print("🔍 Current SSID after connection: '\(currentSSID ?? "none")'")
                            print("🔍 Expected SSID: '\(cleanSSID)'")
                            print("🔍 Actually connected: \(actuallyConnected)")
                            
                            isConnecting = false
                            completion(actuallyConnected)
                        }
                    }
                }
            }
        }
    }
    
    static func getCurrentWiFiSSID() -> String? {
        guard let interfaces = CNCopySupportedInterfaces() as? [String] else {
            print("❌ No supported interfaces")
            return nil
        }
        
        for interface in interfaces {
            guard let info = CNCopyCurrentNetworkInfo(interface as CFString) as? [String: Any] else {
                print("❌ No network info for interface: \(interface)")
                continue
            }
            
            if let ssid = info[kCNNetworkInfoKeySSID as String] as? String {
                print("✅ Found SSID: \(ssid)")
                return ssid
            }
        }
        
        print("❌ No SSID found in any interface")
        return nil
    }
    
    static func testGatewayConnectivity(gateway: String, completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://\(gateway)") else {
            completion(false)
            return
        }
        
        var request = URLRequest(url: url)
        request.timeoutInterval = 2.0
        request.httpMethod = "HEAD" // Lighter request
        
        let task = URLSession.shared.dataTask(with: request) { _, response, error in
            DispatchQueue.main.async {
                if let httpResponse = response as? HTTPURLResponse {
                    // Any HTTP response indicates connectivity
                    print("🔍 Gateway \(gateway) responded with status: \(httpResponse.statusCode)")
                    completion(true)
                } else if let error = error as? URLError {
                    // Check if it's a timeout vs actual connectivity
                    let isConnected = error.code != .timedOut && error.code != .cannotConnectToHost
                    print("🔍 Gateway \(gateway) error: \(error.code.rawValue), connected: \(isConnected)")
                    completion(isConnected)
                } else {
                    print("🔍 Gateway \(gateway) - unknown response")
                    completion(false)
                }
            }
        }
        
        task.resume()
    }
    
    static func extractSerialFromSSID(_ ssid: String) -> String? {
        // Extract serial from "SenchiSetup-1234" format
        if ssid.hasPrefix("SenchiSetup-") {
            return String(ssid.dropFirst("SenchiSetup-".count))
        }
        return nil
    }
}

