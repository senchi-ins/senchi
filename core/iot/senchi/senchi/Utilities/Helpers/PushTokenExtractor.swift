//
//  PushTokenExtractor.swift
//  senchi
//
//  Created by Michael Dawes on 2025-01-14.
//

import SwiftUI
import UIKit

struct PushTokenExtractor: View {
    @StateObject private var pushManager = PushNotificationManager()
    @State private var showingToken = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Push Token Extractor")
                .font(.title)
                .fontWeight(.bold)
            
            Text("This utility helps you extract your device's push token for testing purposes.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text("Authorization Status:")
                    Spacer()
                    Text(statusText)
                        .foregroundColor(statusColor)
                }
                
                if let token = pushManager.pushToken {
                    HStack {
                        Text("Push Token:")
                        Spacer()
                        Button("Show Token") {
                            showingToken = true
                        }
                        .buttonStyle(.borderedProminent)
                    }
                } else {
                    HStack {
                        Text("Push Token:")
                        Spacer()
                        Text("Not available")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
            .background(Color(uiColor: .systemGray6))
            .cornerRadius(10)
            
            if pushManager.authorizationStatus == .notDetermined {
                Button("Request Permission") {
                    Task {
                        do {
                            try await pushManager.requestPermission()
                        } catch {
                            print("Permission request failed: \(error)")
                        }
                    }
                }
                .buttonStyle(.borderedProminent)
            }
            
            if pushManager.pushToken != nil {
                Button("Copy Token to Clipboard") {
                    if let token = pushManager.pushToken {
                        UIPasteboard.general.string = token
                    }
                }
                .buttonStyle(.bordered)
            }
            
            Spacer()
        }
        .padding()
        .alert("Push Token", isPresented: $showingToken) {
            Button("Copy") {
                if let token = pushManager.pushToken {
                    UIPasteboard.general.string = token
                }
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            if let token = pushManager.pushToken {
                Text("Your device push token:\n\n\(token)")
            }
        }
    }
    
    private var statusText: String {
        switch pushManager.authorizationStatus {
        case .notDetermined:
            return "Not Determined"
        case .denied:
            return "Denied"
        case .authorized:
            return "Authorized"
        case .provisional:
            return "Provisional"
        case .ephemeral:
            return "Ephemeral"
        @unknown default:
            return "Unknown"
        }
    }
    
    private var statusColor: Color {
        switch pushManager.authorizationStatus {
        case .authorized, .provisional, .ephemeral:
            return .green
        case .denied:
            return .red
        case .notDetermined:
            return .orange
        @unknown default:
            return .gray
        }
    }
}

#Preview {
    PushTokenExtractor()
} 