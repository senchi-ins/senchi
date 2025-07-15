
import SwiftUI
import Foundation

struct HomeTabContent: View {
    @StateObject private var webSocketManager = WebSocketManager()
    @State private var savingsAmount: Double = 0
    @State private var homeHealthScore: Double = 1.0
    
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
                        Text("Good morning, werwer")
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

