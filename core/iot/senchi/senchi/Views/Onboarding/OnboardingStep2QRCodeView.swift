import SwiftUI

struct OnboardingStep2QRCodeView: View {
    @StateObject private var locationManager = LocationPermissionManager()
    
    var onQRCodeScanned: (String) -> Void
    var onManualConnect: () -> Void
    var onConnected: () -> Void
    var onNextStep: () -> Void
    
    @State private var isShowingScanner = false
    @State private var scannedCode: String? = nil
    @State private var isConnecting = false
    @State private var connectionStatus = ""
    @State private var connectedSSID: String? = nil
    @State private var deviceSerial: String? = nil
    
    var body: some View {
        VStack(spacing: 20) {
            ZStack {
                Circle()
                    .fill(Color.gray.opacity(0.1))
                    .frame(width: 64, height: 64)
                Image(systemName: "qrcode")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 32, height: 32)
                    .foregroundColor(SenchiColors.senchiBlue)
            }
            
            VStack(spacing: 8) {
                Text("Connect Your \(ApplicationConfig.hubName)")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Let's connect your \(ApplicationConfig.hubName) to start monitoring your home.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 16) {
                Text("Connect to Device Network")
                    .font(.headline)
                    .foregroundColor(.black)
                Text("Scan the QR code on your HomeGuard device or manually connect to the WiFi network.")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                
                VStack {
                    if let code = scannedCode {
                        VStack(spacing: 8) {
                            Text("QR Code Scanned!")
                                .font(.caption)
                                .foregroundColor(.green)
                            
                            if isConnecting {
                                ProgressView("Connecting to device...")
                                    .font(.caption2)
                            } else if let ssid = connectedSSID {
                                Text("Connected to: \(ssid)")
                                    .font(.caption2)
                                    .foregroundColor(.green)
                                
                                if let serial = deviceSerial {
                                    Text("Device Serial: \(serial)")
                                        .font(.caption2)
                                        .foregroundColor(.blue)
                                }
                            }
                            
                            if !connectionStatus.isEmpty {
                                Text(connectionStatus)
                                    .font(.caption2)
                                    .foregroundColor(.red)
                            }
                        }
                    } else if isShowingScanner {
                        QRCodeScannerView { code in
                            handleQRCodeScanned(code)
                        }
                        .frame(height: 200)
                        .cornerRadius(12)
                    } else {
                        // Placeholder UI when no scanner is active
                        VStack(spacing: 8) {
                            Image(systemName: "qrcode")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 120, height: 120)
                                .foregroundColor(Color.gray.opacity(0.5))
                                .padding(24)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color.gray.opacity(0.3), style: StrokeStyle(lineWidth: 2, dash: [6]))
                                )
                            Text("QR Code Placeholder")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text("Network: SenchiSetup_12345")
                                .font(.caption2)
                                .foregroundColor(.gray)
                        }
                    }
                    
                    Button(action: { isShowingScanner.toggle() }) {
                        Text(isShowingScanner ? "Cancel Scanner" : "Scan QR Code")
                            .font(.caption)
                            .foregroundColor(.blue)
                            .padding(.top, 4)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(Color.gray.opacity(0.08))
                .cornerRadius(12)
            }
            .padding(16)
            .background(Color.gray.opacity(0.12))
            .cornerRadius(12)
            
            // Single action button that changes based on connection status
            Button(action: {
                if connectedSSID?.hasPrefix("SenchiSetup") == true {
                    // Pass the serial number when connected
                    if let serial = deviceSerial {
                        onQRCodeScanned(serial)
                    }
                    onConnected()
                    onNextStep()
                } else {
                    checkCurrentConnection()
                }
            }) {
                Text(getButtonText())
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(getButtonColor())
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .buttonStyle(NoHighlightButtonStyle())
            .padding(.top, 8)
        }
        .padding(28)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color(.black).opacity(0.05), radius: 10, x: 0, y: 4)
        .padding(.horizontal, 16)
        .padding(.top, 20)
        .onAppear {
            checkCurrentConnection()
        }
    }
    
    // Helper functions for dynamic button
    private func getButtonText() -> String {
        if isConnecting {
            return "Connecting..."
        } else if connectedSSID?.hasPrefix("SenchiSetup") == true {
            return "Continue Setup"
        } else if connectedSSID != nil {
            return "Not Connected to Device"
        } else {
            return "Check Connection"
        }
    }
    
    private func getButtonColor() -> Color {
        if connectedSSID?.hasPrefix("SenchiSetup") == true {
            return SenchiColors.senchiBlue
        } else {
            return Color.gray
        }
    }

    private func handleQRCodeScanned(_ code: String) {
        scannedCode = code
        isShowingScanner = false
        
        // Parse the Wi-Fi QR code
        guard let wifiInfo = WiFiQRHandler.parseWiFiQR(code) else {
            connectionStatus = "Invalid QR code format"
            return
        }
        
        // Extract serial number from password (your approach)
        deviceSerial = wifiInfo.password
        
        // Connect to the Wi-Fi network
        isConnecting = true
        connectionStatus = ""
        
        WiFiQRHandler.connectToWiFi(ssid: wifiInfo.ssid, password: wifiInfo.password) { success in
            isConnecting = false
            
            if success {
                connectedSSID = wifiInfo.ssid
                connectionStatus = ""
                // Pass serial to parent immediately upon successful connection
                onQRCodeScanned(deviceSerial ?? wifiInfo.password)
            } else {
                connectionStatus = "Failed to connect. Try manually connecting to \(wifiInfo.ssid)"
            }
        }
    }
    
    private func checkCurrentConnection() {
        if let currentSSID = WiFiQRHandler.getCurrentWiFiSSID() {
            connectedSSID = currentSSID
            
            if currentSSID.hasPrefix("SenchiSetup") {
                deviceSerial = WiFiQRHandler.extractSerialFromSSID(currentSSID)
                // If we detect we're already connected, pass the serial
                if let serial = deviceSerial {
                    onQRCodeScanned(serial)
                }
            }
        }
    }
}

#Preview {
    OnboardingStep2QRCodeView(
        onQRCodeScanned: { code in
            print("Scanned device serial: \(code)")
        },
        onManualConnect: {
            print("Manual connect requested")
        },
        onConnected: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            print("Moving to next onboarding step")
        },
        onNextStep: {
            print("Moving to next onboarding step")
        }
    )
}
