
import SwiftUI
import Foundation

struct HomeTabContent: View {
    @EnvironmentObject var userSettings: UserSettings
    @EnvironmentObject var pushManager: PushNotificationManager
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var webSocketManager = WebSocketManager(userId: "")
    @State private var savingsAmount: Double = 0
    @State private var homeHealthScore: Double = 1.0
    @State private var testResult: String = ""
    @State private var isTesting: Bool = false
    @State private var selectedProperty: String = "main"
    @State private var showingPropertySelector = false
    
    init() {
        // Initialize with empty user ID - will be updated when available
    }
    
    private func getGreeting() -> String {
        let hour = Calendar.current.component(.hour, from: Date())
        
        switch hour {
        case 5..<12:
            return "Good morning"
        case 12..<17:
            return "Good afternoon"
        case 17..<22:
            return "Good evening"
        default:
            return "Good evening"
        }
    }
    
    private func getUserName() -> String {
        // First try UserSettings (from onboarding)
        if !userSettings.userName.isEmpty {
            return userSettings.userName
        }
        
        // Then try UserDefaults (from login)
        if let storedName = UserDefaults.standard.string(forKey: "user_full_name"), !storedName.isEmpty {
            return storedName
        }
        
        // TODO: Remove this once we have a default user name
        return ""
    }
    
    private func formatPropertyName(_ propertyName: String) -> String {
        return propertyName.replacingOccurrences(of: "_", with: " ")
            .split(separator: " ")
            .map { $0.capitalized }
            .joined(separator: " ")
    }
    
    private func initializeWebSocketManager() {
        // Get user_id from userInfo if available
        if let userInfo = userSettings.userInfo, !userInfo.user_id.isEmpty {
            webSocketManager.updateUserId(userInfo.user_id)
        }
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Connection Status Indicator
                HStack {
                    Circle()
                        .fill(webSocketManager.isConnected ? SenchiColors.senchiGreen : SenchiColors.senchiRed)
                        .frame(width: 12, height: 12)
                    Text(webSocketManager.isConnected ? "Connected" : "Disconnected")
                        .font(.caption)
                        .foregroundColor(.gray)
                    Spacer()
                }
                .padding(.horizontal, 4)
  
                // Greeting
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 4) {
                        // TODO: Change default and set up in db
                        Text("\(getGreeting()), \(getUserName())")
                            .font(.title3).fontWeight(.semibold)
                            .foregroundColor(.black)
                        Text("\(formatPropertyName(selectedProperty)) is protected")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    HStack(spacing: 12) {
//                        ZStack {
//                            Circle().fill(SenchiColors.senchiBlue.opacity(0.08)).frame(width: 36, height: 36)
//                            Image(systemName: "shield.fill")
//                                .foregroundColor(SenchiColors.senchiBlue)
//                        }
                        
                        // Property Selector Button
                        Button(action: {
                            showingPropertySelector = true
                        }) {
                            HStack(spacing: 6) {
                                Image(systemName: "building.2.fill")
                                    .foregroundColor(SenchiColors.senchiBlue)
                                    .font(.caption)
                                Text(formatPropertyName(selectedProperty))
                                    .font(.caption)
                                    .foregroundColor(SenchiColors.senchiBlue)
                                    .lineLimit(1)
                                Image(systemName: "chevron.down")
                                    .font(.caption2)
                                    .foregroundColor(SenchiColors.senchiBlue)
                            }
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(SenchiColors.senchiBlue.opacity(0.1))
                            .cornerRadius(8)
                        }
                    }
                }
                // Health Score
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Home Health Score")
                                .font(.caption)
                                .foregroundColor(.gray)
                            // TODO: Update to read from api
                            HStack(alignment: .center, spacing: 8) {
                                Text("\(homeHealthScore, format: .percent.precision(.fractionLength(0)))")
                                    .font(.title2).fontWeight(.bold)
                                    .foregroundColor(SenchiColors.senchiGrey)
                                Spacer()
                                // TODO: Make this dynamic
//                                HStack(spacing: 4) {
//                                    Image(systemName: "exclamationmark.triangle.fill")
//                                        .foregroundColor(.yellow)
//                                    Text("Good")
//                                        .font(.caption)
//                                        .foregroundColor(.gray)
//                                }
                            }
                        }
                    }
                    ProgressView(value: homeHealthScore)
                        .accentColor(SenchiColors.senchiGrey)
                    Text("Coming soon!")
                        .font(.caption2)
                        .foregroundColor(.gray)
                }
                .padding()
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                // Device/Savings
                HStack(spacing: 16) {
                    VStack {
                        Text("\(webSocketManager.deviceCount)")
                            .font(.title2).fontWeight(.bold)
                            .foregroundColor(.black)
                        Text("Connected Devices")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                    VStack {
                        Text("$\(Int(savingsAmount))")
                            .font(.title2).fontWeight(.bold)
                            .foregroundColor(SenchiColors.senchiBlack)
                        Text("Est. Savings")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                }
                // Connected Devices
                HStack {
                    Text("Connected Devices")
                        .font(.headline)
                        .foregroundColor(.black)
                    Spacer()
                    Button(action: {
                        Task {
                            do {
                                let result = try await permitJoin(duration: 60)
                                print("Permit join successful: \(result)")
                                
                                // Success haptic feedback
                                let generator = UINotificationFeedbackGenerator()
                                generator.notificationOccurred(.success)
                            } catch {
                                print("Permit join failed: \(error)")
                                
                                // Error haptic feedback
                                let generator = UINotificationFeedbackGenerator()
                                generator.notificationOccurred(.error)
                            }
                        }
                    }) {
                        HStack(spacing: 4) {
                            // TODO: Fix colours
                            Image(systemName: "plus.circle.fill").background(Color.white).clipShape(Circle())
                                .foregroundColor(SenchiColors.senchiBlue)
                            Text("Add Device")
                                .foregroundColor(.white)
                        }
                        .font(.subheadline)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(SenchiColors.senchiBlue)
                        .cornerRadius(8)
                    }
                }
                // Device Cards from API
                VStack(spacing: 12) {
                    ForEach(webSocketManager.devices) { device in
                        DeviceCardView(device: device)
                    }
                }
            }
            .padding(20)
        }
        .refreshable {
            webSocketManager.reconnect()
        }
        .onAppear {
            initializeWebSocketManager()
            
            webSocketManager.fetchDevices()
            Task {
                savingsAmount = await calculateSavings()
            }
        }
        .onReceive(userSettings.$userInfo) { newUserInfo in
            // Setup WebSocket when userInfo becomes available
            if newUserInfo != nil {
                initializeWebSocketManager()
            }
        }
        .sheet(isPresented: $showingPropertySelector) {
            PropertySelectorView(
                selectedProperty: $selectedProperty,
                onPropertySelected: { newProperty in
                    selectedProperty = newProperty
                    // Update WebSocket manager with new property
                    webSocketManager.updateProperty(newProperty)
                }
            )
        }
    }
}

struct PropertySelectorView: View {
    @Binding var selectedProperty: String
    let onPropertySelected: (String) -> Void
    @EnvironmentObject var userSettings: UserSettings
    @Environment(\.dismiss) private var dismiss
    
    private func formatPropertyName(_ propertyName: String) -> String {
        return propertyName.replacingOccurrences(of: "_", with: " ")
            .split(separator: " ")
            .map { $0.capitalized }
            .joined(separator: " ")
    }
    `
    private var properties: [String] {
        getProperties(userId: (userSettings.userInfo?.user_id ?? "") as String)
    }
    
    var body: some View {
        NavigationView {
            List {
                ForEach(properties, id: \.self) { property in
                    Button(action: {
                        onPropertySelected(property)
                        dismiss()
                    }) {
                        HStack(spacing: 12) {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(formatPropertyName(property))
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                Text("Property description")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                            if property == selectedProperty {
                                Image(systemName: "checkmark")
                                    .foregroundColor(SenchiColors.senchiBlue)
                                    .font(.headline)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                
                Section {
                    Button(action: {
                        // TODO: Add new property functionality
                        print("Add new property")
                    }) {
                        HStack(spacing: 12) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(SenchiColors.senchiBlue)
                                .font(.headline)
                            Text("Add New Property")
                                .foregroundColor(SenchiColors.senchiBlue)
                                .font(.headline)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Select Property")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

