
import SwiftUI

struct AccountSettings: View {
    // MARK: - Beta Placeholder (Original implementation commented out below)
    
    @EnvironmentObject private var userSettings: UserSettings
    @EnvironmentObject private var authManager: AuthManager
    @State private var showingReconnectionModal = false
    
    var body: some View {
        NavigationView {
            ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header
                VStack(alignment: .leading, spacing: 4) {
                    Text("Settings")
                        .font(.title2).fontWeight(.bold).foregroundColor(.black)
                    Text("Manage your account and preferences")
                        .font(.subheadline).foregroundColor(.gray)
                }
                .padding(.top, 8)
                
                // Beta Placeholder
                VStack(spacing: 16) {
                    Image(systemName: "gearshape.fill")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 60, height: 60)
                        .foregroundColor(.gray.opacity(0.5))
                    
                    Text("Settings Coming Soon")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.black)
                    
                    Text("Account management, notifications, and activity logs will be available in the next update.")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                    
                    VStack(spacing: 8) {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Account profile management")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Notification preferences")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Activity logs and history")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Support and help center")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    }
                    .padding(.top, 8)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
                .background(Color.gray.opacity(0.05))
                .cornerRadius(16)
                
                Button(action: {
                    showingReconnectionModal = true
                }) {
                    HStack {
                        Text("Reconnect \(ApplicationConfig.hubName)").fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(SenchiColors.senchiBlue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                
                Button(action: {
                    Task {
                        // Clear the keychain by calling logout on AuthManager
                        authManager.logout()
                        
                        // Update user settings
                        userSettings.loggedIn = false
                        
                        print("✅ Sign out completed - keychain cleared and user logged out")
                    }
                }) {
                    HStack {
                        Image(systemName: "arrow.right.square.fill")
                        Text("Sign Out").fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                
                // Delete account
                Button(action: {
                    Task {
                        try await authManager.deleteAccount()
                        
                        // Update user settings
                        userSettings.loggedIn = false
                    }
                }) {
                    HStack {
                        Image(systemName: "arrow.right.square.fill")
                        Text("Delete account").fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                
                // Version
                Text("HomeGuard v0.0.1")
                    .font(.caption2).foregroundColor(.gray)
                    .frame(maxWidth: .infinity, alignment: .center)
            }
            .padding(20)
            }
            .background(Color.white.ignoresSafeArea())
        }
        .sheet(isPresented: $showingReconnectionModal) {
            DeviceReconnectionModal()
        }
    }
}

/*
// MARK: - Original Implementation (Commented out for beta)
private struct ToggleRow: View {
    var title: String
    var subtitle: String
    @Binding var isOn: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack {
                Text(title).font(.subheadline).foregroundColor(.black)
                Spacer()
                Toggle("", isOn: $isOn).labelsHidden()
            }
            Text(subtitle).font(.caption).foregroundColor(.gray)
        }
    }
}
*/

/*
private struct ActivityLogRow: View {
    enum LogType { case warning, critical, info }
    var icon: String
    var title: String
    var subtitle: String
    var date: String
    var type: LogType
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: icon)
                .foregroundColor(color)
                .font(.title3)
                .padding(.top, 2)
            VStack(alignment: .leading, spacing: 2) {
                HStack {
                    Text(title).font(.subheadline).foregroundColor(.black).lineLimit(1)
                    Spacer()
                    if type == .warning {
                        LabelTag(text: "warning", color: .yellow, textColor: .black)
                    } else if type == .critical {
                        LabelTag(text: "critical", color: SenchiColors.senchiRed, textColor: .white)
                    } else if type == .info {
                        LabelTag(text: "info", color: SenchiColors.senchiBlue, textColor: .white)
                    }
                }
                Text(subtitle).font(.caption).foregroundColor(.gray).lineLimit(1)
                Text(date).font(.caption2).foregroundColor(.gray)
            }
        }
        .padding(10)
        .background(Color.gray.opacity(0.08))
        .cornerRadius(10)
    }
    private var color: Color {
        switch type {
        case .warning: return .yellow
        case .critical: return SenchiColors.senchiRed
        case .info: return SenchiColors.senchiBlue
        }
    }
}
*/

/*
private struct LabelTag: View {
    var text: String
    var color: Color
    var textColor: Color
    var body: some View {
        Text(text)
            .font(.caption2).fontWeight(.bold)
            .padding(.horizontal, 8)
            .padding(.vertical, 2)
            .background(color)
            .foregroundColor(textColor)
            .cornerRadius(6)
    }
}

private struct SettingsLinkRow: View {
    var title: String
    var body: some View {
        HStack {
            Text(title).font(.subheadline).foregroundColor(.black)
            Spacer()
            Image(systemName: "chevron.right").foregroundColor(.gray)
        }
        .padding(.vertical, 8)
    }
}
*/

#Preview {
    AccountSettings()
}
