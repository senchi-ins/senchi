//
//  HomeMonitorApp.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import SwiftUI

@main
struct HomeMonitorApp: App {
    
    @StateObject private var appDelegate = AppDelegate()
    @StateObject private var authManager = AuthManager()
    @StateObject private var pushManager = PushNotificationManager()
    @StateObject private var userSettings = UserSettings()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(UserSettings())
                .environmentObject(authManager)
                .environmentObject(pushManager)
                .onAppear {
                    pushManager.setAuthManager(authManager)
                    appDelegate.pushNotificationManager = pushManager
                    UIApplication.shared.delegate = appDelegate
                    
                    // Verify setup on launch
                    Task {
                        await verifySetupOnLaunch()
                    }
                }
        }
    }
    
    private func verifySetupOnLaunch() async {
        if authManager.isAuthenticated {
            let isValid = await authManager.verifyToken()
            if isValid {
                print("User authenticated and token valid")
            } else {
                print("Token expired, user needs to re-authenticate")
            }
        } else {
            print("User not authenticated, needs device setup")
        }
    }
}
