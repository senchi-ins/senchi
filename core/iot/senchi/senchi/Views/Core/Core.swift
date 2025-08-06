
import SwiftUI

struct HomeDashboardView: View {
    @State private var selectedTab: Int = 0
    var body: some View {
        VStack(spacing: 0) {
            Group {
                switch selectedTab {
                case 0:
                    HomeTabContent()
                case 1:
                    External()
                case 2:
                    //HealthSavings()
                    // TODO: Make this only show in specific circumstances
                    Prediction(
                        predictionRationale: PredictionRationale.mockData()
                    )                                                                       
                case 3:
                    AccountSettings()
                default:
                    HomeTabContent()
                }
            }
            MainTabBar(selectedTab: $selectedTab)
        }
        .background(Color.white.ignoresSafeArea())
        .ignoresSafeArea(.keyboard, edges: .bottom)
        .onReceive(NotificationCenter.default.publisher(for: .navigateToTab)) { notification in
            print("Core.swift received navigateToTab notification with object: \(notification.object ?? "nil")")
            print("Current selectedTab before change: \(selectedTab)")
            
            DispatchQueue.main.async {
                if let tabIndex = notification.object as? Int {
                    print("Setting selectedTab to: \(tabIndex)")
                    selectedTab = tabIndex
                } else {
                    selectedTab = 2
                    print("Failed to extract tabIndex from notification object, defaulting to 2")
                }
                print("selectedTab is now: \(selectedTab)")
            }
        }
    }
}

extension Notification.Name {
    static let navigateToTab = Notification.Name("navigateToTab")
}

#Preview {
    HomeDashboardView()
}
