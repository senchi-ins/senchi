import SwiftUI

struct OnboardingViewMain: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var userSettings: UserSettings
    
    @State private var fullName: String = ""
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var currentStep: Int = 1
    @State private var showDashboard: Bool = false
    @State private var isSigningIn: Bool = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var deviceSerial: String = ""
    @State private var isLoading = false
    @State private var showLoginView = false
    
    private let totalSteps: Int = 4
    
    @FocusState private var focusedField: Field?
    enum Field: Hashable {
        case fullName, email, password
    }
    
    var body: some View {
        if showDashboard {
            HomeDashboardView()
        } else {
            VStack {
                ProgressView(value: Double(currentStep), total: Double(totalSteps))
                    .accentColor(SenchiColors.senchiBlue)
                    .padding(.top, 32)
                    .padding(.horizontal, 32)
                
                Text("Step \(currentStep) of \(totalSteps)")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .padding(.top, 8)
                
                Spacer(minLength: 32)
                
                currentStepView
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color.white.ignoresSafeArea())
            .alert("Alert", isPresented: $showingAlert) {
                Button("OK") { }
            } message: {
                Text(alertMessage)
            }
            .sheet(isPresented: $showLoginView) {
                LoginView()
            }
            .overlay(
                Group {
                    if isLoading {
                        Color.black.opacity(0.3)
                            .ignoresSafeArea()
                        ProgressView("Processing...")
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(1.5)
                    }
                }
            )
        }
    }

    @ViewBuilder
    private var currentStepView: some View {
        Group {
            switch currentStep {
            case 1:
                OnboardingStep1AccountView(
                    fullName: $fullName,
                    email: $email,
                    password: $password,
                    focusedField: $focusedField,
                    onCreateAccount: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        createAccount()
                    },
                    onSignIn: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        userSettings.isOnboarded = true
                        signIn()
                    },
                    onLogin: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        userSettings.isOnboarded = true
                        showLoginView = true
                    }
                )
            case 2:
                OnboardingStep2QRCodeView(
                    onQRCodeScanned: { code in
                        deviceSerial = code  // Use the actual device serial from QR code
                    },
                    onManualConnect: {
                        // Handle manual connect
                    },
                    onConnected: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        withAnimation { currentStep = 3 }
                    },
                    onNextStep: {
                        // This will be handled by onConnected
                    }
                )
            case 3:
                OnboardingStep3MainWifi(
                    onConnected: {
                        withAnimation { currentStep = 4 }
                    }
                )
            case 4:
                OnboardingStep4Confirmation(
                    deviceSerial: deviceSerial,
                    onGoToDashboard: {
                        setupDevice()
                        userSettings.isOnboarded = true
                        withAnimation { showDashboard = true }
                    }
                )
            default:
                Text("Onboarding Complete!")
            }
        }
        .animation(.easeInOut, value: currentStep)
        .transition(.asymmetric(insertion: .move(edge: .trailing), removal: .move(edge: .leading)))
    }
    
    private func createAccount() {
        guard !fullName.isEmpty && !email.isEmpty && !password.isEmpty else {
            alertMessage = "Please fill in all fields"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        Task {
            do {
                try await authManager.createAccount(
                    fullName: fullName,
                    email: email,
                    password: password
                )
                
                await MainActor.run {
                    // Store the user name for use throughout the app
                    userSettings.userName = fullName
                    isLoading = false
                    alertMessage = "Account created successfully!"
                    showingAlert = true
                    withAnimation { currentStep = 2 }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    alertMessage = "Account creation failed: \(error.localizedDescription)"
                    showingAlert = true
                }
            }
        }
    }
    
    private func signIn() {
        guard !email.isEmpty && !password.isEmpty else {
            alertMessage = "Please enter email and password"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        Task {
            do {
                try await authManager.signIn(email: email, password: password)
                
                await MainActor.run {
                    isLoading = false
                    alertMessage = "Signed in successfully!"
                    showingAlert = true
                    withAnimation { currentStep = 2 }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    alertMessage = "Sign in failed: \(error.localizedDescription)"
                    showingAlert = true
                }
            }
        }
    }
    
    private func setupDevice() {
        guard !deviceSerial.isEmpty else {
            alertMessage = "Please scan the QR code on your device first"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        Task {
            do {
                // Now setup device with the actual device serial from QR code and user's email
                try await authManager.setupDevice(serialNumber: deviceSerial, email: email, fullName: fullName)
                
                await MainActor.run {
                    isLoading = false
                    // Device setup is now complete, go to dashboard
                    withAnimation { showDashboard = true }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    alertMessage = "Device setup failed: \(error.localizedDescription)"
                    showingAlert = true
                }
            }
        }
    }
}

#Preview {
    OnboardingViewMain()
        .environmentObject(AuthManager())
}
