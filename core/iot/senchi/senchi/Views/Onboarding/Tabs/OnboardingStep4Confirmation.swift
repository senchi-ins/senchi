import SwiftUI

struct OnboardingStep4Confirmation: View {
    @EnvironmentObject var pushManager: PushNotificationManager
    @State private var notificationPermissionGranted = false
    @State private var isRequestingPermission = false
    
    var deviceSerial: String = ""
    var onGoToDashboard: () -> Void = {}
    
    var body: some View {
        VStack(spacing: 24) {
            Spacer(minLength: 32)
            ZStack {
                Circle()
                    .fill(Color.green.opacity(0.12))
                    .frame(width: 64, height: 64)
                Image(systemName: "checkmark.circle.fill")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 40, height: 40)
                    .foregroundColor(.green)
            }
            VStack(spacing: 8) {
                Text("Setup Complete!")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Your HomeGuard system is now protecting your home.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
                            HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "checkmark.square.fill")
                        .foregroundColor(.green)
                        .font(.title3)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Device Connected")
                            .font(.headline)
                            .foregroundColor(.green)
                        Text("Your \(ApplicationConfig.hubName) is online and monitoring your home's health.")
                            .font(.caption)
                            .foregroundColor(.green)
                        if !deviceSerial.isEmpty {
                            Text("Device ID: \(deviceSerial)")
                                .font(.caption2)
                                .foregroundColor(.blue)
                        }
                    }
                }
                .padding(14)
                .background(Color.green.opacity(0.10))
                .cornerRadius(10)
            VStack(spacing: 10) {
                HStack {
                    Text("Network Status")
                        .font(.subheadline)
                    Spacer()
                    Text("Connected")
                        .font(.subheadline)
                        .foregroundColor(.green)
                }
                HStack {
                    Text("Device Health")
                        .font(.subheadline)
                    Spacer()
                    Text("Excellent")
                        .font(.subheadline)
                        .foregroundColor(.green)
                }
                HStack {
                    Text("Monitoring")
                        .font(.subheadline)
                    Spacer()
                    Text("Active")
                        .font(.subheadline)
                        .foregroundColor(.green)
                }
            }
            .padding(.horizontal, 8)
            Button(action: onGoToDashboard) {
                HStack {
                    Image(systemName: "house.fill")
                    Text("Go to Dashboard")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(SenchiColors.senchiBlue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .padding(.top, 8)
            
            // Notification Permission Section
            VStack(spacing: 12) {
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: notificationPermissionGranted ? "bell.fill" : "bell.slash")
                        .foregroundColor(notificationPermissionGranted ? .green : .orange)
                        .font(.title3)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Leak Alerts")
                            .font(.headline)
                            .foregroundColor(.black)
                        Text("Get instant notifications when leaks are detected in your home.")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
                .padding(14)
                .background(notificationPermissionGranted ? Color.green.opacity(0.10) : Color.orange.opacity(0.10))
                .cornerRadius(10)
                
                if !notificationPermissionGranted {
                    Button(action: requestNotificationPermission) {
                        HStack {
                            if isRequestingPermission {
                                ProgressView()
                                    .scaleEffect(0.8)
                            } else {
                                Image(systemName: "bell.badge")
                            }
                            Text(isRequestingPermission ? "Requesting..." : "Enable Leak Alerts")
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(SenchiColors.senchiBlue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                    .disabled(isRequestingPermission)
                }
            }
            
            Spacer()
        }
        .padding(28)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color(.black).opacity(0.05), radius: 10, x: 0, y: 4)
        .padding(.horizontal, 16)
        .padding(.top, 20)
        .onAppear {
            checkNotificationStatus()
        }
    }
    
    private func checkNotificationStatus() {
        notificationPermissionGranted = pushManager.authorizationStatus == .authorized
    }
    
    private func requestNotificationPermission() {
        isRequestingPermission = true
        
        Task {
            do {
                try await pushManager.requestPermission()
                await MainActor.run {
                    notificationPermissionGranted = true
                    isRequestingPermission = false
                }
            } catch {
                await MainActor.run {
                    isRequestingPermission = false
                    // Show error or continue without notifications
                }
            }
        }
    }
}
