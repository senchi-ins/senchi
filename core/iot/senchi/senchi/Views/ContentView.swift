
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var userSettings: UserSettings
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var pushManager: PushNotificationManager
    
    var body: some View {
        Group {
            if authManager.isAuthenticated || userSettings.loggedIn {
                // Your main app interface
                HomeDashboardView()
            } else {
                // User needs to create account/sign in
                OnboardingViewMain()
            }
        }
    }
}
