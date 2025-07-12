import SwiftUI
import Foundation
import NetworkExtension
import SystemConfiguration.CaptiveNetwork


struct WiFiQRHandler {
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
        let hotspotConfig = NEHotspotConfiguration(ssid: ssid, passphrase: password, isWEP: false)
        hotspotConfig.joinOnce = true // Don't save permanently
        
        NEHotspotConfigurationManager.shared.apply(hotspotConfig) { error in
            DispatchQueue.main.async {
                if let error = error {
                    print("WiFi connection error: \(error.localizedDescription)")
                    completion(false)
                } else {
                    print("Successfully connected to \(ssid)")
                    completion(true)
                }
            }
        }
    }
    
    static func getCurrentWiFiSSID() -> String? {
        guard let interfaces = CNCopySupportedInterfaces() as? [String] else { return nil }
        
        for interface in interfaces {
            guard let info = CNCopyCurrentNetworkInfo(interface as CFString) as? [String: Any],
                  let ssid = info[kCNNetworkInfoKeySSID as String] as? String else {
                continue
            }
            return ssid
        }
        return nil
    }
    
    static func extractSerialFromSSID(_ ssid: String) -> String? {
        // Extract serial from "SenchiSetup-1234" format
        if ssid.hasPrefix("SenchiSetup-") {
            return String(ssid.dropFirst("SenchiSetup-".count))
        }
        return nil
    }
}

