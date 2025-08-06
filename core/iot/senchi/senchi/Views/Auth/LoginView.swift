import SwiftUI

struct LoginView: View {
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String = ""
    @State private var showAlert: Bool = false
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var userSettings: UserSettings
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Header
                VStack(spacing: 16) {
                    Image(systemName: "house.fill")
                        .font(.system(size: 60))
                        .foregroundColor(SenchiColors.senchiBlue)
                    
                    Text("Welcome Back")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.black)
                    
                    Text("Sign in to access your home monitoring dashboard")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                }
                
                // Login Form
                VStack(spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Email")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.black)
                        
                        TextField("Enter your email", text: $email)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.emailAddress)
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Password")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.black)
                        
                        SecureField("Enter your password", text: $password)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                    }
                    
                    Button(action: {
                        Task {
                            await login()
                        }
                    }) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .scaleEffect(0.8)
                                    .foregroundColor(.white)
                            } else {
                                Image(systemName: "arrow.right")
                            }
                            Text(isLoading ? "Signing In..." : "Sign In")
                        }
                        .foregroundColor(.white)
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(SenchiColors.senchiBlue)
                        .cornerRadius(12)
                    }
                    .disabled(email.isEmpty || isLoading)
                    
                    if !errorMessage.isEmpty {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                            .multilineTextAlignment(.center)
                    }
                }
                
                Spacer()
                
                // Footer
                VStack(spacing: 12) {
                    Text("Don't have an account?")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    
                    Button("Set up a new device") {
                        dismiss()
                    }
                    .font(.subheadline)
                    .foregroundColor(SenchiColors.senchiBlue)
                }
            }
            .padding(.horizontal, 30)
            .padding(.vertical, 20)
            .navigationBarHidden(true)
        }
        .alert("Login Error", isPresented: $showAlert) {
            Button("OK") { }
        } message: {
            Text(errorMessage)
        }
    }
    
    private func login() async {
        guard !email.isEmpty else {
            errorMessage = "Please enter your email"
            return
        }
        guard !password.isEmpty else {
            errorMessage = "Please enter your password"
            return
        }
        
        isLoading = true
        errorMessage = ""
        print(password)
        
        do {
            let info = try await authManager.loginWithEmail(email: email, password: password)
            userSettings.userInfo = info
        } catch {
            errorMessage = error.localizedDescription
            showAlert = true
        }
        
        userSettings.isOnboarded = true
        isLoading = false
        print(userSettings.isOnboarded)
        print(authManager.isAuthenticated)
        dismiss()
    }
}

#Preview {
    LoginView()
} 
