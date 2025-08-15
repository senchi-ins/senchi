import SwiftUI
import AVFoundation
import NetworkExtension
import SystemConfiguration.CaptiveNetwork

struct DeviceReconnectionModal: View {
    @Environment(\.dismiss) private var dismiss
    
    @State private var currentStep: ReconnectionStep = .qrCode
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
    
    // WiFi configuration states
    @State private var ssid: String = ""
    @State private var password: String = ""
    @State private var isWiFiConfiguring = false
    @State private var wifiConfigStatus = ""
    @FocusState private var focusedField: FocusField?
    
    enum FocusField: Hashable {
        case ssid, password
    }
    
    enum ReconnectionStep {
        case qrCode
        case wifiSetup
        case success
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header
                HStack {
                    Button("Cancel") {
                        dismiss()
                    }
                    .foregroundColor(.blue)
                    
                    Spacer()
                    
                    Text("Reconnect Device")
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Spacer()
                    
                    // Progress indicator
                    HStack(spacing: 4) {
                        Circle()
                            .fill(currentStep == .qrCode ? SenchiColors.senchiBlue : Color.gray.opacity(0.3))
                            .frame(width: 8, height: 8)
                        Circle()
                            .fill(currentStep == .wifiSetup ? SenchiColors.senchiBlue : Color.gray.opacity(0.3))
                            .frame(width: 8, height: 8)
                        Circle()
                            .fill(currentStep == .success ? SenchiColors.senchiBlue : Color.gray.opacity(0.3))
                            .frame(width: 8, height: 8)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 16)
                
                Divider()
                
                // Content
                ScrollView {
                    VStack(spacing: 24) {
                        switch currentStep {
                        case .qrCode:
                            qrCodeStepView
                        case .wifiSetup:
                            wifiSetupStepView
                        case .success:
                            successStepView
                        }
                    }
                    .padding(20)
                }
            }
            .background(Color.white)
        }
        .onAppear {
            checkCurrentConnection()
        }
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
            checkCurrentConnection()
            if showingConnectionHelp, let expectedSSID = scannedSSID {
                checkConnectionAfterManual()
            }
        }
    }
    
    // MARK: - QR Code Step
    private var qrCodeStepView: some View {
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
                Text("Connect to Device")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Scan the QR code on your \(ApplicationConfig.hubName) to connect.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 16) {
                Text("Device Network")
                    .font(.headline)
                    .foregroundColor(.black)
                Text("Scan the QR code on your device or manually connect to the WiFi network.")
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
            
            Button(action: {
                if connectedSSID?.hasPrefix("SenchiSetup") == true {
                    withAnimation {
                        currentStep = .wifiSetup
                    }
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
    }
    
    // MARK: - WiFi Setup Step
    private var wifiSetupStepView: some View {
        VStack(spacing: 20) {
            ZStack {
                Circle()
                    .fill(Color.gray.opacity(0.1))
                    .frame(width: 64, height: 64)
                Image(systemName: "wifi")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 32, height: 32)
                    .foregroundColor(SenchiColors.senchiBlue)
            }
            
            VStack(spacing: 8) {
                Text("Configure Home WiFi")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Connect your \(ApplicationConfig.hubName) to your home WiFi network.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("WiFi Network Name (SSID)")
                        .font(.caption)
                        .foregroundColor(.gray)
                    TextField("Enter your WiFi network name", text: $ssid)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(focusedField == .ssid ? SenchiColors.senchiBlue : Color.gray.opacity(0.3), lineWidth: 2)
                        )
                        .focused($focusedField, equals: .ssid)
                        .tint(.black)
                        .disableAutocorrection(true)
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("WiFi Password")
                        .font(.caption)
                        .foregroundColor(.gray)
                    SecureField("Enter your WiFi password", text: $password)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(focusedField == .password ? SenchiColors.senchiBlue : Color.gray.opacity(0.3), lineWidth: 2)
                        )
                        .focused($focusedField, equals: .password)
                        .tint(.black)
                        .disableAutocorrection(true)
                }
            }
            
            HStack(alignment: .top, spacing: 8) {
                Image(systemName: "lightbulb.fill")
                    .foregroundColor(.yellow)
                Text("Your device will restart and connect to your home network. This may take a few moments.")
                    .font(.caption)
                    .foregroundColor(.blue)
            }
            .padding(12)
            .background(Color.blue.opacity(0.08))
            .cornerRadius(8)
            
            if !wifiConfigStatus.isEmpty {
                Text(wifiConfigStatus)
                    .font(.caption)
                    .foregroundColor(isWiFiConfiguring ? .orange : .green)
                    .multilineTextAlignment(.center)
                    .padding(.top, 8)
            }
            
            Button(action: {
                configureWiFi()
            }) {
                HStack {
                    if isWiFiConfiguring {
                        ProgressView()
                            .scaleEffect(0.8)
                            .foregroundColor(.white)
                    }
                    Text(isWiFiConfiguring ? "Configuring..." : "Connect to Home WiFi")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(SenchiColors.senchiBlue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .buttonStyle(NoHighlightButtonStyle())
            .disabled(isWiFiConfiguring || ssid.isEmpty || password.isEmpty)
        }
    }
    
    // MARK: - Success Step
    private var successStepView: some View {
        VStack(spacing: 20) {
            ZStack {
                Circle()
                    .fill(Color.green.opacity(0.1))
                    .frame(width: 64, height: 64)
                Image(systemName: "checkmark.circle.fill")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 32, height: 32)
                    .foregroundColor(.green)
            }
            
            VStack(spacing: 8) {
                Text("Device Reconnected!")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Your \(ApplicationConfig.hubName) has been successfully reconnected to your home network.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            Button(action: {
                dismiss()
            }) {
                Text("Done")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(SenchiColors.senchiBlue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .buttonStyle(NoHighlightButtonStyle())
            .padding(.top, 8)
        }
    }
    
    // MARK: - Helper Functions
    private func getButtonText() -> String {
        if isConnecting {
            return "Connecting..."
        } else if connectedSSID?.hasPrefix("SenchiSetup") == true {
            return "Continue to WiFi Setup"
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
            } else if attempt < maxAttempts {
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                    self.attemptConnection(ssid: ssid, password: password, attempt: attempt + 1, maxAttempts: maxAttempts)
                }
            } else {
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
    
    private func handleSuccessfulConnection(ssid: String) {
        isConnecting = false
        connectedSSID = ssid
        connectionStatus = ""
        connectionFailed = false
        showingConnectionHelp = false
        
        if let serial = WiFiQRHandler.extractSerialFromSSID(ssid) {
            deviceSerial = serial
        }
    }
    
    private func checkConnectionAfterManual() {
        if let currentSSID = WiFiQRHandler.getCurrentWiFiSSID() {
            if let expectedSSID = scannedSSID {
                if currentSSID == expectedSSID {
                    handleSuccessfulConnection(ssid: expectedSSID)
                    return
                }
            }
        }
        
        connectionStatus = "Still not connected. Please try again."
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
        if let currentSSID = WiFiQRHandler.getCurrentWiFiSSID() {
            connectedSSID = currentSSID
            
            if currentSSID.hasPrefix("SenchiSetup") {
                deviceSerial = WiFiQRHandler.extractSerialFromSSID(currentSSID)
            }
        } else {
            connectedSSID = nil
        }
    }
    
    private func configureWiFi() {
        guard !ssid.isEmpty && !password.isEmpty else { return }
        
        isWiFiConfiguring = true
        wifiConfigStatus = "Configuring WiFi..."
        
        senchi.configureWiFi(ssid: ssid, password: password) { result in
            DispatchQueue.main.async {
                self.isWiFiConfiguring = false
                
                switch result {
                case .success(_):
                    self.wifiConfigStatus = "WiFi configured successfully!"
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                        withAnimation {
                            self.currentStep = .success
                        }
                    }
                case .failure(let error):
                    self.wifiConfigStatus = "Configuration failed: \(error.localizedDescription)"
                }
            }
        }
    }
}

#Preview {
    DeviceReconnectionModal()
}
