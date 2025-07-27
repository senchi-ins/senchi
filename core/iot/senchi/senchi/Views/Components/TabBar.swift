
import SwiftUI

struct MainTabBar: View {
    @Binding var selectedTab: Int
    var body: some View {
        HStack {
            TabBarButton(icon: "house.fill", label: "Home", selected: selectedTab == 0) { selectedTab = 0 }
            TabBarButton(icon: "heart.fill", label: "Health & Savings", selected: selectedTab == 1) { selectedTab = 1 }
            TabBarButton(icon: "gearshape.fill", label: "Settings", selected: selectedTab == 2) { selectedTab = 2 }
            TabBarButton(icon: "shield.fill", label: "External", selected: selectedTab == 3) { selectedTab = 3 }
        }
        .padding(.vertical, 8)
        .background(Color.white)
        .overlay(Rectangle().frame(width: nil, height: 1, alignment: .top).foregroundColor(Color.gray.opacity(0.2)), alignment: .top)
        .ignoresSafeArea(.keyboard, edges: .bottom)
    }
}

private struct TabBarButton: View {
    var icon: String
    var label: String
    var selected: Bool
    var action: () -> Void
    var body: some View {
        Button(action: action) {
            VStack(spacing: 2) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(selected ? SenchiColors.senchiBlue : .gray)
                Text(label)
                    .font(.caption)
                    .foregroundColor(selected ? SenchiColors.senchiBlue : .gray)
            }
            .frame(maxWidth: .infinity)
        }
    }
}
