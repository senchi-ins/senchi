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
    @State private var showingConnectionHelp = false
    @State private var connectionFailed = false
    @State private var scannedSSID: String? = nil
    @State private var scannedPassword: String? = nil
    
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
                            HStack {
                                Text("QR Code Scanned!")
                                    .font(.caption)
                                    .foregroundColor(.green)
                                
                                Spacer()
                                
                                Button("Scan Again") {
                                    resetConnection()
                                }
                                .font(.caption)
                                .foregroundColor(.blue)
                            }
                            
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
                                    .foregroundColor(connectionFailed ? .red : .orange)
                                    .multilineTextAlignment(.leading)
                            }
                            
                            // Show manual connection help if needed
                            if showingConnectionHelp {
                                VStack(spacing: 12) {
                                    Divider()
                                    
                                    Text("Manual Connection Steps:")
                                        .font(.caption)
                                        .fontWeight(.semibold)
                                        .foregroundColor(.orange)
                                    
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("1. Open Settings → WiFi")
                                        Text("2. Select '\(scannedSSID ?? "SenchiSetup")'")
                                        Text("3. Enter password: '\(scannedPassword ?? "")'")
                                        Text("4. Return to this app")
                                    }
                                    .font(.caption2)
                                    .foregroundColor(.gray)
                                    
                                    HStack(spacing: 12) {
                                        Button("Open Settings") {
                                            if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
                                                UIApplication.shared.open(settingsUrl)
                                            }
                                        }
                                        .font(.caption)
                                        .padding(.horizontal, 12)
                                        .padding(.vertical, 6)
                                        .background(Color.blue)
                                        .foregroundColor(.white)
                                        .cornerRadius(6)
                                        
                                        Button("I've Connected") {
                                            checkConnectionAfterManual()
                                        }
                                        .font(.caption)
                                        .padding(.horizontal, 12)
                                        .padding(.vertical, 6)
                                        .background(Color.green)
                                        .foregroundColor(.white)
                                        .cornerRadius(6)
                                    }
                                }
                                .padding(.top, 8)
                            }
                            
                            // Retry button for failed connections
                            if connectionFailed && !showingConnectionHelp {
                                Button("Try Again") {
                                    retryConnection()
                                }
                                .font(.caption)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(6)
                                .padding(.top, 4)
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
                        }
                    }
                    
                    Button(action: {
                        if scannedCode != nil {
                            resetConnection()
                        } else {
                            isShowingScanner.toggle()
                        }
                    }) {
                        Text(getScannerButtonText())
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
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
            // Check if user connected while in Settings
            print("🔍 App returned from background, checking connection...")
            checkCurrentConnection()
            
            if showingConnectionHelp, let expectedSSID = scannedSSID {
                checkConnectionAfterManual()
            }
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
    
    private func getScannerButtonText() -> String {
        if scannedCode != nil {
            return "Scan Different QR Code"
        } else if isShowingScanner {
            return "Cancel Scanner"
        } else {
            return "Scan QR Code"
        }
    }
    
    private func resetConnection() {
        scannedCode = nil
        isShowingScanner = false
        isConnecting = false
        connectionStatus = ""
        connectedSSID = nil
        deviceSerial = nil
        showingConnectionHelp = false
        connectionFailed = false
        scannedSSID = nil
        scannedPassword = nil
    }

    private func handleQRCodeScanned(_ code: String) {
        scannedCode = code
        isShowingScanner = false
        
        guard let wifiInfo = WiFiQRHandler.parseWiFiQR(code) else {
            connectionStatus = "Invalid QR code format"
            connectionFailed = true
            return
        }
        
        deviceSerial = wifiInfo.password
        scannedSSID = wifiInfo.ssid
        scannedPassword = wifiInfo.password
        isConnecting = true
        connectionStatus = "Connecting to device..."
        connectionFailed = false
        showingConnectionHelp = false
        
        // Fixed the typo: max -> maxAttempts
        let maxAttempts: Int = 1
        attemptConnection(ssid: wifiInfo.ssid, password: wifiInfo.password, attempt: 1, maxAttempts: maxAttempts)
    }
    
    private func attemptConnection(ssid: String, password: String, attempt: Int, maxAttempts: Int) {
        connectionStatus = "Connecting... (attempt \(attempt)/\(maxAttempts))"
        
        WiFiQRHandler.connectToWiFi(ssid: ssid, password: password) { success in
            if success {
                self.isConnecting = false
                self.connectedSSID = ssid
                self.connectionStatus = ""
                self.connectionFailed = false
                self.showingConnectionHelp = false
                self.onQRCodeScanned(self.deviceSerial ?? password)
            } else if attempt < maxAttempts {
                // Wait and retry
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                    self.attemptConnection(ssid: ssid, password: password, attempt: attempt + 1, maxAttempts: maxAttempts)
                }
            } else {
                // All attempts failed - show in-app instructions
                self.isConnecting = false
                self.connectionFailed = true
                self.showInAppConnectionInstructions(ssid: ssid, password: password)
            }
        }
    }
    
    private func showInAppConnectionInstructions(ssid: String, password: String) {
        isConnecting = false
        connectionStatus = "Automatic connection failed"
        showingConnectionHelp = true
    }
    
    // Removed the problematic startPollingForConnection function
    // that was causing repeated nehelper errors
    
    private func handleSuccessfulConnection(ssid: String) {
        print("🎉 Handling successful connection to: \(ssid)")
        isConnecting = false
        connectedSSID = ssid
        connectionStatus = ""
        connectionFailed = false
        showingConnectionHelp = false
        
        // Extract serial from SSID or use the stored password
        if let serial = WiFiQRHandler.extractSerialFromSSID(ssid) {
            deviceSerial = serial
            print("🔍 Extracted serial from SSID: \(serial)")
        } else if let storedSerial = deviceSerial {
            print("🔍 Using stored serial: \(storedSerial)")
        }
        
        if let serial = deviceSerial {
            print("🔍 Calling onQRCodeScanned with serial: \(serial)")
            onQRCodeScanned(serial)
        }
    }
    
    private func checkConnectionAfterManual() {
        print("🔍 Checking connection after manual setup...")
        
        if let currentSSID = WiFiQRHandler.getCurrentWiFiSSID() {
            print("🔍 Current SSID: '\(currentSSID)'")
            if let expectedSSID = scannedSSID {
                print("🔍 Expected SSID: '\(expectedSSID)'")
                if currentSSID == expectedSSID {
                    print("✅ Manual connection successful!")
                    handleSuccessfulConnection(ssid: expectedSSID)
                    return
                }
            }
        } else {
            print("🔍 No current SSID detected")
        }
        
        connectionStatus = "Still not connected. Please try again."
        print("❌ Manual connection check failed")
    }
    
    private func retryConnection() {
        guard let ssid = scannedSSID, let password = scannedPassword else { return }
        
        isConnecting = true
        connectionStatus = "Retrying connection..."
        connectionFailed = false
        showingConnectionHelp = false
        
        attemptConnection(ssid: ssid, password: password, attempt: 1, maxAttempts: 3)
    }
    
    private func checkCurrentConnection() {
        print("🔍 Checking current connection...")
        
        if let currentSSID = WiFiQRHandler.getCurrentWiFiSSID() {
            print("🔍 Current SSID detected: '\(currentSSID)'")
            connectedSSID = currentSSID
            
            if currentSSID.hasPrefix("SenchiSetup") {
                print("🔍 Connected to SenchiSetup network!")
                deviceSerial = WiFiQRHandler.extractSerialFromSSID(currentSSID)
                
                // If we detect we're already connected, pass the serial
                if let serial = deviceSerial {
                    print("🔍 Auto-detected serial: \(serial)")
                    onQRCodeScanned(serial)
                }
            }
        } else {
            print("🔍 No current SSID detected")
            connectedSSID = nil
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
