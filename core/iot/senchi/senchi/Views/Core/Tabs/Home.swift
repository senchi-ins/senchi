
import SwiftUI
import Foundation
import UIKit

struct HomeTabContent: View {
    @StateObject private var webSocketManager = WebSocketManager()
    @EnvironmentObject var userSettings: UserSettings
    @EnvironmentObject var pushManager: PushNotificationManager
    @State private var savingsAmount: Double = 0
    @State private var homeHealthScore: Double = 1.0
    @State private var testResult: String = ""
    @State private var isTesting: Bool = false
    
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
                
                // Test Buttons Section
                VStack(spacing: 12) {
                    Button("Debug Push Token") {
                        pushManager.debugPushTokenStatus()
                        testResult = "Debug info printed to console"
                    }
                    .buttonStyle(.bordered)
                    // TODO: Delete
                    Button("Test APS Environment") {
                        Task {
                            await pushManager.cleanPushNotificationTest()
                        }
                    }
                    
                    
                    Button("Manual Register") {
                        pushManager.manuallyRegisterForNotifications()
                        testResult = "Manual registration triggered"
                    }
                    .buttonStyle(.bordered)
                    
                    Button("Test APNs Connectivity") {
                        APNsConnectivityTest.testAPNsConnectivity()
                        testResult = "APNs connectivity test started"
                    }
                    .buttonStyle(.bordered)
                    
                    Button("Test Push Token") {
                        if let token = pushManager.pushToken {
                            print("📱 Current push token: \(token)")
                            // Copy to clipboard
                            UIPasteboard.general.string = token
                            testResult = "Token copied to clipboard!"
                        } else {
                            testResult = "No push token available"
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    
                    if !testResult.isEmpty {
                        Text(testResult)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
//                VStack(alignment: .leading, spacing: 12) {
//                    Text("Development Tests")
//                        .font(.headline)
//                        .foregroundColor(.black)
//                    
//                    HStack(spacing: 12) { 
//                        Button(action: {
//                            Task {
//                                isTesting = true
//                                isTesting = false
//                            }
//                        }) {
//                            HStack(spacing: 4) {
//                                if isTesting {
//                                    ProgressView()
//                                        .scaleEffect(0.8)
//                                } else {
//                                    Image(systemName: "wrench.and.screwdriver")
//                                }
//                                Text("Test Device Setup")
//                            }
//                            .foregroundColor(.white)
//                            .font(.subheadline)
//                            .padding(.horizontal, 12)
//                            .padding(.vertical, 8)
//                            .background(SenchiColors.senchiBlue)
//                            .cornerRadius(8)
//                        }
//                        .disabled(isTesting)
//                        
//                        Button(action: {
//                            Task {
//                                isTesting = true
//                                isTesting = false
//                            }
//                        }) {
//                            HStack(spacing: 4) {
//                                if isTesting {
//                                    ProgressView()
//                                        .scaleEffect(0.8)
//                                } else {
//                                    Image(systemName: "envelope.fill")
//                                }
//                                Text("Clean Redis")
//                            }
//                            .foregroundColor(.white)
//                            .font(.subheadline)
//                            .padding(.horizontal, 12)
//                            .padding(.vertical, 8)
//                            .background(SenchiColors.senchiGreen)
//                            .cornerRadius(8)
//                        }
//                        .disabled(isTesting)
//                    }
//                    
//                    if !testResult.isEmpty {
//                        Text(testResult)
//                            .font(.caption)
//                            .foregroundColor(testResult.hasPrefix("✅") ? .green : .red)
//                            .padding(8)
//                            .background(Color.gray.opacity(0.1))
//                            .cornerRadius(6)
//                    }
//                }
//                .padding()
//                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
//                
                // Greeting
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 4) {
                        // TODO: Change default and set up in db
                        Text("\(getGreeting()), \(getUserName())")
                            .font(.title3).fontWeight(.semibold)
                            .foregroundColor(.black)
                        Text("Your home is protected")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    ZStack {
                        Circle().fill(SenchiColors.senchiBlue.opacity(0.08)).frame(width: 36, height: 36)
                        Image(systemName: "shield.fill")
                            .foregroundColor(SenchiColors.senchiBlue)
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
            webSocketManager.fetchDevices()
            Task {
                savingsAmount = await calculateSavings()
            }
        }
    }
}

