
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var userSettings: UserSettings
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var pushManager: PushNotificationManager
    
    @State private var showingLeakAlert = false
    @State private var leakAlertData: [AnyHashable: Any] = [:]
    
    var body: some View {
        Group {
            if authManager.isAuthenticated || userSettings.isOnboarded {
                HomeDashboardView()
            } else {
                OnboardingViewMain()
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .showLeakAlert)) { notification in
            if let data = notification.object as? [AnyHashable: Any] {
                leakAlertData = data
                showingLeakAlert = true
            }
        }
        .sheet(isPresented: $showingLeakAlert) {
            LeakAlertView(
                deviceName: leakAlertData["device_name"] as? String ?? "Unknown Device",
                location: leakAlertData["location"] as? String ?? "Unknown Location",
                timestamp: Date(),
                onDismiss: {
                    showingLeakAlert = false
                }
            )
        }
    }
}
