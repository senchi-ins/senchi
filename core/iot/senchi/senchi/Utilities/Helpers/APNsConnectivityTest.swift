//
//  APNsConnectivityTest.swift
//  senchi
//
//  Created by Michael Dawes on 2025-01-14.
//

import Foundation
import Network

class APNsConnectivityTest {
    
    static func testAPNsConnectivity() {
        print("🔍 Testing APNs connectivity...")
        
        // Test sandbox APNs endpoint
        let sandboxURL = "api.sandbox.push.apple.com"
        let productionURL = "api.push.apple.com"
        
        testConnection(to: sandboxURL, name: "Sandbox APNs")
        testConnection(to: productionURL, name: "Production APNs")
    }
    
    private static func testConnection(to host: String, name: String) {
        let connection = NWConnection(host: NWEndpoint.Host(host), port: NWEndpoint.Port(integerLiteral: 443), using: .tls)
        
        connection.stateUpdateHandler = { state in
            switch state {
            case .ready:
                print("✅ \(name): Connected successfully")
            case .failed(let error):
                print("❌ \(name): Connection failed - \(error)")
            case .waiting(let error):
                print("⏳ \(name): Waiting - \(error)")
            case .cancelled:
                print("🚫 \(name): Connection cancelled")
            default:
                print("🔄 \(name): State changed to \(state)")
            }
        }
        
        connection.start(queue: .global())
        
        // Cancel after 5 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
            connection.cancel()
        }
    }
} 