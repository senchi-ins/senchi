
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
                    HealthSavings()
                case 2:
                    AccountSettings()
                case 3:
                    External()
                default:
                    HomeTabContent()
                }
            }
            MainTabBar(selectedTab: $selectedTab)
        }
        .background(Color.white.ignoresSafeArea())
        .ignoresSafeArea(.keyboard, edges: .bottom)
    }
}

#Preview {
    HomeDashboardView()
}
