//
//  AppDelegate.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-14.
//

import SwiftUI

class AppDelegate: NSObject, UIApplicationDelegate, ObservableObject {
    @Published var pushNotificationManager = PushNotificationManager()
    
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        // Configure push notifications
        UNUserNotificationCenter.current().delegate = self
        return true
    }
    
    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        print("✅ AppDelegate: didRegisterForRemoteNotificationsWithDeviceToken called!")
        print("✅ Device token data length: \(deviceToken.count) bytes")
        pushNotificationManager.handleDeviceToken(deviceToken)
        print(deviceToken)
    }
    
    func application(_ application: UIApplication,
                     didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("❌ AppDelegate: didFailToRegisterForRemoteNotificationsWithError called!")
        print("❌ Error: \(error.localizedDescription)")
        pushNotificationManager.handleRegistrationError(error)
    }
}

extension AppDelegate: UNUserNotificationCenterDelegate {
    // Handle notification when app is in foreground
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                               willPresent notification: UNNotification,
                               withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        // Show notification even when app is active
        completionHandler([.banner, .sound, .badge])
    }
    
    // Handle notification tap
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                               didReceive response: UNNotificationResponse,
                               withCompletionHandler completionHandler: @escaping () -> Void) {
        let userInfo = response.notification.request.content.userInfo
        print("Notification tapped: \(userInfo)")
        
        // Handle notification tap based on type
        if let notificationType = userInfo["type"] as? String {
            handleNotificationTap(type: notificationType, data: userInfo)
        }
        
        completionHandler()
    }
    
    private func handleNotificationTap(type: String, data: [AnyHashable: Any]) {
        switch type {
        case "leak_alert":
            // Navigate to leak alert screen
            NotificationCenter.default.post(name: .showLeakAlert, object: data)
        case "device_update":
            // Navigate to device status screen
            NotificationCenter.default.post(name: .showDeviceUpdate, object: data)
        default:
            print("Unknown notification type: \(type)")
        }
    }
}
