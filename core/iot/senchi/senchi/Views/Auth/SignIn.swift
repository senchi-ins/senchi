//
//  SignIn.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-14.
//

import SwiftUI

struct SignInView: View {
    @Binding var email: String
    @Binding var password: String
    @FocusState.Binding var focusedField: OnboardingViewMain.Field?
    var onSignIn: () -> Void
    var onCreateAccount: () -> Void
    
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
                Text("Welcome Back")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                Text("Sign in to your HomeGuard account")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 16) {
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
                    SecureField("Enter your password", text: $password)
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
            
            Button(action: onSignIn) {
                Text("Sign In")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(SenchiColors.senchiBlue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .buttonStyle(NoHighlightButtonStyle())
            .padding(.top, 8)
            
            Button(action: onCreateAccount) {
                Text("Don't have an account? Create one")
                    .font(.footnote)
                    .foregroundColor(.black)
                    .padding(.top, 4)
            }
            .buttonStyle(NoHighlightButtonStyle())
        }
        .padding(32)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color(.black).opacity(0.05), radius: 10, x: 0, y: 4)
        .padding(.horizontal, 16)
        .padding(.top, 32)
    }
}
