//
//  PushManager.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-14.
//

import SwiftUI

@MainActor
class PushNotificationManager: NSObject, ObservableObject {
    @Published var pushToken: String?
    @Published var authorizationStatus: UNAuthorizationStatus = .notDetermined
    
    private weak var authManager: AuthManager?
    private weak var userSettings: UserSettings?
    
    override init() {
        super.init()
        print(pushToken)
        checkAuthorizationStatus()
    }
    
    func setAuthManager(_ authManager: AuthManager) {
        self.authManager = authManager
    }
    
    func checkAuthorizationStatus() {
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            DispatchQueue.main.async {
                self.authorizationStatus = settings.authorizationStatus
            }
        }
    }
    func sendTokenToServer(_ deviceToken: String) async {
        guard let url = URL(string: "\(ApplicationConfig.zbAPIBase)/api/register-device") else { return }
        
        // Get the current token
        guard let token = authManager?.currentToken else {
            print("❌ No authentication token available for device registration")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let payload = [
            "device_token": deviceToken,
            "user_id": userSettings?.userInfo?.user_id ?? "",
            "device_type": "ios"
        ]
        
        print("🔍 Sending device registration payload: \(payload)")
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🔍 Device registration response status: \(httpResponse.statusCode)")
                if let responseString = String(data: data, encoding: .utf8) {
                    print("🔍 Device registration response: \(responseString)")
                }
                
                if 200...299 ~= httpResponse.statusCode {
                    print("✅ Device token registered successfully")
                } else {
                    print("❌ Device registration failed with status: \(httpResponse.statusCode)")
                }
            }
        } catch {
            print("❌ Error sending token to server: \(error)")
        }
        await authManager?.updatePushToken(deviceToken)
    }
    
    func requestPermission() async throws {
        let center = UNUserNotificationCenter.current()
        
        print("🔔 Requesting push notification permission...")
        let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
        
        await MainActor.run {
            self.authorizationStatus = granted ? .authorized : .denied
        }
        
        if granted {
            await MainActor.run {
                UIApplication.shared.registerForRemoteNotifications()
            }
        } else {
            // TODO: Fix the error type
            // throw AuthError.pushNotificationDenied
        }
    }
    
    func handleDeviceToken(_ deviceToken: Data) {
        let tokenString = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        self.pushToken = tokenString
        UserDefaults.standard.set(tokenString, forKey: "previous_push_token")
        
        Task {
            await sendTokenToServer(tokenString)
        }
    }
    
    func sendPendingTokenIfNeeded() async {
        if let pendingToken = UserDefaults.standard.string(forKey: "pending_push_token") {
            await sendTokenToServer(pendingToken)
            UserDefaults.standard.removeObject(forKey: "pending_push_token")
        } else if let currentToken = pushToken {
            // Re-send current token to make sure server has it
            await sendTokenToServer(currentToken)
        }
    }
    
    func handleRegistrationError(_ error: Error) {
        print("Failed to register for push notifications: \(error)")
    }
    
    func debugPushTokenStatus() {
        print("🔍 Push Token Debug Info:")
        print("  - Authorization Status: \(authorizationStatus.rawValue)")
        print("  - Push Token Available: \(pushToken != nil)")
        print("  - Push Token: \(pushToken ?? "nil")")
        print("  - Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
        
        // Check embedded provisioning profile
        if let provisioningPath = Bundle.main.path(forResource: "embedded", ofType: "mobileprovision") {
            print("  - Provisioning Profile: Found")
            // You can read more details from the provisioning profile if needed
        } else {
            print("  - Provisioning Profile: Not found (check signing)")
        }
        
        // Check entitlements
        if let entitlements = Bundle.main.entitlements {
            print("  - Entitlements available: \(entitlements.count > 0)")
            if let apsEnv = entitlements["aps-environment"] as? String {
                print("  - APS Environment: \(apsEnv)")
            } else {
                print("  - APS Environment: Not configured")
            }
        }
        
        // Check if we're registered
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            DispatchQueue.main.async {
                print("  - Notification Settings:")
                print("    - Authorization: \(settings.authorizationStatus.rawValue)")
                print("    - Alert Setting: \(settings.alertSetting.rawValue)")
                print("    - Sound Setting: \(settings.soundSetting.rawValue)")
                print("    - Badge Setting: \(settings.badgeSetting.rawValue)")
            }
        }
    }
}

extension Bundle {
    var entitlements: [String: Any]? {
        guard let path = Bundle.main.path(forResource: "entitlements", ofType: "plist") else {
            return nil
        }
        return NSDictionary(contentsOfFile: path) as? [String: Any]
    }
}

extension PushNotificationManager: UNUserNotificationCenterDelegate {
    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification) async -> UNNotificationPresentationOptions {
    return [.badge, .banner, .list, .sound]
    }
}
