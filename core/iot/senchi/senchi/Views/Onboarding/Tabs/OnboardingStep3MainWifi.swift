//
//  OnboardingStep3MainWifi.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import SwiftUI


struct OnboardingStep3MainWifi: View {
    @State private var ssid: String = ""
    @State private var password: String = ""
    @State private var isConnected: Bool = false
    @FocusState private var focusedField: FocusField?
    
    enum FocusField: Hashable {
        case ssid, password
    }
    
    var onConnected: () -> Void
    
    var body: some View {
        if isConnected {
            // TODO: Remove this
        } else {
            VStack(spacing: 24) {
                Spacer(minLength: 32)
                wifiIcon
                titleSection
                wifiForm
                infoBox
                connectButton
                Spacer()
            }
            .padding(28)
            .background(Color.white)
            .cornerRadius(20)
            .shadow(color: Color(.black).opacity(0.05), radius: 10, x: 0, y: 4)
            .padding(.horizontal, 16)
            .padding(.top, 20)
        }
    }
    
    private var wifiIcon: some View {
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
    }
    
    private var titleSection: some View {
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
    }
    
    private var wifiForm: some View {
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
    }
    
    private var infoBox: some View {
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
    }
    
    private var connectButton: some View {
        Button(action: {
            // Simulate connection and navigate to home
            isConnected = true
        }) {
            Text("Connect to Home WiFi")
                .frame(maxWidth: .infinity)
                .padding()
                .background(SenchiColors.senchiBlue)
                .foregroundColor(.white)
                .cornerRadius(8)
        }
        .buttonStyle(PlainButtonStyle())
    }
}
