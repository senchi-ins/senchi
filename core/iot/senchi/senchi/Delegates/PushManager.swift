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
        
        let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
        
        await MainActor.run {
            self.authorizationStatus = granted ? .authorized : .denied
        }
        
        if granted {
            await MainActor.run {
                UIApplication.shared.registerForRemoteNotifications()
            }
        } else {
            throw AuthError.pushNotificationDenied
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
}
