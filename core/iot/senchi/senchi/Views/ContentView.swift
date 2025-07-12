//
//  ContentView.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var userSettings: UserSettings
    
    var body: some View {
        if userSettings.loggedIn {
            HomeDashboardView()
        } else {
            OnboardingView()
        }
    }
}

#Preview {
    ContentView()
}
