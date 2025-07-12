import SwiftUI

struct OnboardingView: View {
    @State private var fullName: String = ""
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var currentStep: Int = 1
    private let totalSteps: Int = 3
    
    @FocusState private var focusedField: Field?
    enum Field: Hashable {
        case fullName, email, password
    }
    
    var body: some View {
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
        .background(Color(.systemGray6).opacity(0.5).ignoresSafeArea())
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
                    focusedField: _focusedField,
                    onCreateAccount: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        withAnimation { currentStep = 2 }
                    },
                    onSignIn: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        // Navigate to sign in
                    }
                )
            case 2:
                OnboardingStep2QRCodeView(
                    onQRCodeScanned: { code in
                        // Handle scanned QR code
                    },
                    onManualConnect: {
                        // Handle manual connect
                    },
                    onConnected: {
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                        // TODO: Move to next onboarding step
                    },
                    onNextStep: {
                        withAnimation { currentStep = 3 }
                    }
                )
            case 3:
                OnboardingStep3MainWifi(
                    onConnected: {
                        //
                    }
                )
            default:
                Text("Onboarding Complete!")
            }
        }
        .animation(.easeInOut, value: currentStep)
        .transition(.asymmetric(insertion: .move(edge: .trailing), removal: .move(edge: .leading)))
    }
}

#Preview {
    OnboardingView()
} 
