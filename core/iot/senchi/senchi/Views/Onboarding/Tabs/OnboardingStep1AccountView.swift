import SwiftUI


struct OnboardingStep1AccountView: View {
    @Binding var fullName: String
    @Binding var email: String
    @Binding var password: String
    
    @FocusState.Binding var focusedField: OnboardingViewMain.Field?
    var onCreateAccount: () -> Void
    var onSignIn: () -> Void
    var onLogin: () -> Void
    
    var body: some View {
        VStack(spacing: 24) {
            ZStack {
                Circle()
                    .fill(Color.gray.opacity(0.1))
                    .frame(width: 64, height: 64)
                Image(systemName: "shield")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 32, height: 32)
                    .foregroundColor(SenchiColors.senchiBlue)
            }
            
            VStack(spacing: 8) {
                Text("Welcome to HomeGuard")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Your home's health monitoring system. Let's get you started.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Full Name")
                        .font(.caption)
                        .foregroundColor(.gray)
                    TextField("Enter your full name", text: $fullName)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(focusedField == .fullName ? SenchiColors.senchiBlue : Color.gray.opacity(0.3), lineWidth: 2)
                        )
                        .focused($focusedField, equals: .fullName)
                        .tint(.black)
                        .autocapitalization(.words)
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("Email")
                        .font(.caption)
                        .foregroundColor(.gray)
                    TextField("Enter your email", text: $email)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(focusedField == .email ? SenchiColors.senchiBlue : Color.gray.opacity(0.3), lineWidth: 2)
                        )
                        .focused($focusedField, equals: .email)
                        .tint(.black)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("Password")
                        .font(.caption)
                        .foregroundColor(.gray)
                    SecureField("Create a password", text: $password)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(focusedField == .password ? SenchiColors.senchiBlue : Color.gray.opacity(0.3), lineWidth: 2)
                        )
                        .focused($focusedField, equals: .password)
                        .tint(.black)
                }
            }
            
            Button(action: onCreateAccount) {
                Text("Create Account")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(SenchiColors.senchiBlue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .buttonStyle(NoHighlightButtonStyle())
            .padding(.top, 8)
            
            HStack(spacing: 16) {
                Button(action: onSignIn) {
                    Text("Sign In")
                        .font(.footnote)
                        .foregroundColor(.black)
                }
                .buttonStyle(NoHighlightButtonStyle())
                
                Button(action: onLogin) {
                    Text("Login with Email")
                        .font(.footnote)
                        .foregroundColor(SenchiColors.senchiBlue)
                }
                .buttonStyle(NoHighlightButtonStyle())
            }
            .padding(.top, 4)
        }
        .padding(32)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color(.black).opacity(0.05), radius: 10, x: 0, y: 4)
        .padding(.horizontal, 16)
        .padding(.top, 32)
    }
}
