//
//  HomeMonitorApp.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import SwiftUI

@main
struct HomeMonitorApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(UserSettings())
        }
    }
}
