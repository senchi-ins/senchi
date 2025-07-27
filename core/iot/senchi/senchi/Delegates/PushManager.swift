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
    
    override init() {
        super.init()
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
    
    func requestPermission() async throws {
        let center = UNUserNotificationCenter.current()
        
        print("🔔 Requesting push notification permission...")
        let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
        
        await MainActor.run {
            self.authorizationStatus = granted ? .authorized : .denied
            print("🔔 Permission granted: \(granted)")
        }
        
        if granted {
            await MainActor.run {
                print("🔔 Registering for remote notifications...")
                UIApplication.shared.registerForRemoteNotifications()
            }
        } else {
            print("❌ Push notification permission denied")
            // TODO: Fix the error type
            // throw AuthError.pushNotificationDenied
        }
    }
    
    func handleDeviceToken(_ deviceToken: Data) {
        let tokenString = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        self.pushToken = tokenString
        print("📱 Received push token: \(tokenString)")
        
        // Update token with auth manager
        Task {
            await authManager?.updatePushToken(tokenString)
        }
    }
    
    func handleRegistrationError(_ error: Error) {
        print("❌ Failed to register for push notifications: \(error)")
    }
    
    func manuallyRegisterForNotifications() {
        print("🔔 Manually registering for push notifications...")
        
        // First, check current settings
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            DispatchQueue.main.async {
                print("🔍 Current notification settings:")
                print("  - Authorization: \(settings.authorizationStatus.rawValue)")
                print("  - Alert: \(settings.alertSetting.rawValue)")
                print("  - Sound: \(settings.soundSetting.rawValue)")
                print("  - Badge: \(settings.badgeSetting.rawValue)")
                
                // Only register if authorized
                if settings.authorizationStatus == .authorized {
                    print("🔔 Authorization confirmed, registering for remote notifications...")
                    print("🔍 Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
                    print("🔍 Team ID: \(Bundle.main.infoDictionary?["CFBundleTeamIdentifier"] as? String ?? "unknown")")
                    print("🔍 App Version: \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown")")
                    print("🔍 Build Version: \(Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "unknown")")
                    
                    // Check if we have a valid team ID
                    if let teamID = Bundle.main.infoDictionary?["CFBundleTeamIdentifier"] as? String, teamID != "unknown" {
                        print("✅ Team ID is properly configured: \(teamID)")
                    } else {
                        print("❌ Team ID is missing - check Xcode signing configuration")
                        print("🔍 Full bundle info for debugging:")
                        if let bundleInfo = Bundle.main.infoDictionary {
                            for (key, value) in bundleInfo {
                                if key.contains("CFBundle") || key.contains("Team") {
                                    print("  - \(key): \(value)")
                                }
                            }
                        }
                    }
                    
                    UIApplication.shared.registerForRemoteNotifications()
                } else {
                    print("❌ Not authorized for notifications")
                }
            }
        }
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
    
    func testPushRegistration() async {
        print("🧪 === PUSH NOTIFICATION REGISTRATION TEST ===")
        
        // Check current state
        await MainActor.run {
            print("📊 Current state:")
            print("  - Authorization: \(authorizationStatus.rawValue)")
            print("  - Has token: \(pushToken != nil)")
            print("  - Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
            
            // Check APS environment
            if let apsEnv = Bundle.main.object(forInfoDictionaryKey: "aps-environment") as? String {
                print("  - APS Environment: \(apsEnv)")
            } else {
                print("  - APS Environment: ❌ NOT FOUND")
            }
        }
        
        // Ensure we have permission
        if authorizationStatus != .authorized {
            print("\n🔐 Requesting permission...")
            do {
                try await requestPermission()
                print("✅ Permission granted")
            } catch {
                print("❌ Permission failed: \(error)")
                return
            }
        }
        
        // Clear any existing token to test fresh registration
        await MainActor.run {
            pushToken = nil
            print("\n🔄 Cleared existing token, attempting fresh registration...")
            
            // Unregister first
            UIApplication.shared.unregisterForRemoteNotifications()
            print("📤 Unregistered from remote notifications")
        }
        
        // Wait a moment then re-register
        try? await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds
        
        await MainActor.run {
            print("📥 Registering for remote notifications...")
            print("👀 WATCH CONSOLE FOR AppDelegate callbacks:")
            print("   - Success: 'didRegisterForRemoteNotificationsWithDeviceToken'")
            print("   - Failure: 'didFailToRegisterForRemoteNotificationsWithError'")
            
            UIApplication.shared.registerForRemoteNotifications()
        }
        
        // Check result after delay
        try? await Task.sleep(nanoseconds: 15_000_000_000) // 15 seconds
        
        await MainActor.run {
            print("\n📋 FINAL RESULT:")
            if let token = pushToken {
                print("🎉 SUCCESS! Token: \(token)")
            } else {
                print("❌ FAILED - No token received")
                print("💡 If you didn't see any AppDelegate callbacks, there might be a connection issue")
            }
        }
    }
    
    func cleanPushNotificationTest() async {
        print("🧹 === CLEAN PUSH NOTIFICATION TEST ===")
        
        // Step 1: Verify bundle ID matches Apple Developer account
        let bundleID = Bundle.main.bundleIdentifier ?? "unknown"
        print("📱 Bundle ID: \(bundleID)")
        print("⚠️ CRITICAL: This MUST exactly match your Apple Developer App ID")
        print("   Expected: com.mdawes.senchi")
        print("   Actual:   \(bundleID)")
        
        if bundleID != "com.mdawes.senchi" {
            print("❌ BUNDLE ID MISMATCH!")
            print("🔧 Fix: Change Bundle ID in Xcode to match Apple Developer account")
            return
        }
        
        // Step 2: Request permission
        print("\n🔐 Requesting notification permission...")
        do {
            try await requestPermission()
            print("✅ Permission granted")
        } catch {
            print("❌ Permission failed: \(error)")
            return
        }
        
        // Step 3: Register with detailed logging
        await MainActor.run {
            print("\n📱 Device Info:")
            print("  - Model: \(UIDevice.current.model)")
            print("  - iOS: \(UIDevice.current.systemVersion)")
            
            #if targetEnvironment(simulator)
            print("  - Platform: ❌ SIMULATOR (push won't work!)")
            return
            #else
            print("  - Platform: ✅ Physical Device")
            #endif
            
            print("\n🔄 Registering for push notifications...")
            print("👀 Watch for AppDelegate callbacks:")
            
            // Clear any existing state
            self.pushToken = nil
            
            // Register
            UIApplication.shared.registerForRemoteNotifications()
        }
        
        // Step 4: Wait and report
        try? await Task.sleep(nanoseconds: 15_000_000_000) // 15 seconds
        
        await MainActor.run {
            if let token = pushToken {
                print("\n🎉 SUCCESS!")
                print("📱 Device Token: \(token)")
            } else {
                print("\n❌ FAILED - No device token received")
                print("\n🔍 If you saw NO AppDelegate callbacks, check:")
                print("1. Bundle ID matches Apple Developer App ID exactly")
                print("2. Internet connection is working")
                print("3. Not on restrictive corporate network")
                print("4. Apple Developer account has push notifications enabled")
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
