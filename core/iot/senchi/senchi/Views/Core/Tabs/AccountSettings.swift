
import SwiftUI


struct AccountSettings: View {
    @EnvironmentObject private var userSettings: UserSettings
    
    @State private var pushNotifications = true
    @State private var emailAlerts = true
    @State private var maintenanceReminders = true
    @State private var weeklyReports = false
    var body: some View {
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
                // Account Section
                VStack(alignment: .leading, spacing: 12) {
                    HStack(spacing: 8) {
                        Image(systemName: "person.circle").foregroundColor(.gray)
                        Text("Account").font(.headline).foregroundColor(.black)
                    }
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Michael Anthony Dawes").fontWeight(.semibold).foregroundColor(.black)
                            Text("qweq").font(.caption).foregroundColor(.gray)
                        }
                        Spacer()
                        Image(systemName: "chevron.right").foregroundColor(.gray)
                    }
                    Divider()
                    HStack {
                        Text("Plan").font(.subheadline).foregroundColor(.gray)
                        Spacer()
                        Text("HomeGuard Pro")
                            .font(.caption)
                            .fontWeight(.bold)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(SenchiColors.senchiBlue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    HStack {
                        Text("Member since").font(.subheadline).foregroundColor(.gray)
                        Spacer()
                        Text("January 2024").font(.subheadline).foregroundColor(.black)
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(14)
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                // Notifications Section
                VStack(alignment: .leading, spacing: 12) {
                    HStack(spacing: 8) {
                        Image(systemName: "bell").foregroundColor(.gray)
                        Text("Notifications").font(.headline).foregroundColor(.black)
                    }
                    Text("Control how you receive alerts and updates")
                        .font(.subheadline).foregroundColor(.gray)
                    ToggleRow(title: "Push Notifications", subtitle: "Receive alerts on your device", isOn: $pushNotifications)
                    ToggleRow(title: "Email Alerts", subtitle: "Critical alerts via email", isOn: $emailAlerts)
                    ToggleRow(title: "Maintenance Reminders", subtitle: "Scheduled maintenance notifications", isOn: $maintenanceReminders)
                    ToggleRow(title: "Weekly Reports", subtitle: "Summary of your home's health", isOn: $weeklyReports)
                }
                .padding()
                .background(Color.white)
                .cornerRadius(14)
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                // Activity Log Section
                VStack(alignment: .leading, spacing: 12) {
                    HStack(spacing: 8) {
                        Image(systemName: "clock").foregroundColor(.gray)
                        Text("Activity Log").font(.headline).foregroundColor(.black)
                    }
                    Text("Recent alerts and system events")
                        .font(.subheadline).foregroundColor(.gray)
                    // TODO: Replact this with live data
                    VStack(spacing: 10) {
                        ActivityLogRow(icon: "exclamationmark.triangle.fill", title: "High humidity detected in basement", subtitle: "Basement Moisture sensor reported 68% humidity", date: "7/11/2024 06:30 AM", type: .warning)
                        ActivityLogRow(icon: "wrench.and.screwdriver.fill", title: "HVAC filter replacement due", subtitle: "Scheduled maintenance reminder", date: "7/10/2024 05:00 AM", type: .info)
                        ActivityLogRow(icon: "drop.fill", title: "Water leak detected in kitchen", subtitle: "Kitchen Water Sensor triggered leak alarm", date: "7/9/2024 10:45 AM", type: .critical)
                        ActivityLogRow(icon: "bolt.horizontal.fill", title: "New device connected", subtitle: "Main Circuit Monitor successfully added to network", date: "7/8/2024 12:20 PM", type: .info)
                        ActivityLogRow(icon: "thermometer.sun.fill", title: "Temperature spike in living room", subtitle: "Living Room Sensor detected temperature above normal range", date: "7/7/2024 09:15 AM", type: .warning)
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(14)
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                // Support Section
                VStack(alignment: .leading, spacing: 0) {
                    HStack(spacing: 8) {
                        Image(systemName: "questionmark.circle").foregroundColor(.gray)
                        Text("Support").font(.headline).foregroundColor(.black)
                    }
                    SettingsLinkRow(title: "Help Center")
                    SettingsLinkRow(title: "Contact Support")
                    SettingsLinkRow(title: "Privacy Policy")
                    SettingsLinkRow(title: "Terms of Service")
                }
                .padding()
                .background(Color.white)
                .cornerRadius(14)
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                // Sign Out
                Button(action: {
                    // TODO: Properly handle sign out
                    userSettings.loggedIn = false
                }) {
                    HStack {
                        Image(systemName: "arrow.right.square.fill")
                        Text("Sign Out").fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(SenchiColors.senchiRed)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                // Version
                Text("HomeGuard v\(ApplicationConfig.version)")
                    .font(.caption2).foregroundColor(.gray)
                    .frame(maxWidth: .infinity, alignment: .center)
            }
            .padding(20)
        }
        .background(SenchiColors.senchiBackground.ignoresSafeArea())
    }
}

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

#Preview {
    AccountSettings()
}
