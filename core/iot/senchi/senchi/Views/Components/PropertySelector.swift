//
//  PropertySelector.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-28.
//

import SwiftUI
import Foundation

struct PropertySelectorView: View {
    @Binding var selectedProperty: String
    let onPropertySelected: (String) -> Void
    @EnvironmentObject var userSettings: UserSettings
    @EnvironmentObject var authManager: AuthManager
    @Environment(\.dismiss) private var dismiss
    @State private var newPropertyName: String = ""
    @State private var showingAddPropertySheet = false
    
    private func formatPropertyName(_ propertyName: String) -> String {
        return propertyName.replacingOccurrences(of: "_", with: " ")
            .split(separator: " ")
            .map { $0.capitalized }
            .joined(separator: " ")
    }
    @State private var properties: [String] = []
    
    private func loadProperties() {
        Task {
            do {
                let propertyNames = try await getPropertyNames(
                    userId: userSettings.userInfo?.user_id ?? "",
                    authManager: authManager
                )
                await MainActor.run {
                    self.properties = propertyNames
                }
            } catch {
                print("❌ Failed to load properties: \(error)")
                // Fallback to default properties
                await MainActor.run {
                    self.properties = ["Main"]
                }
            }
        }
    }
    
    var body: some View {
        NavigationView {
            List {
                ForEach(properties, id: \.self) { property in
                    PropertyRowView(
                        property: property,
                        isSelected: property == selectedProperty,
                        onSelect: {
                            onPropertySelected(property)
                            dismiss()
                        }
                    )
                }
                
                Section {
                    Button(action: {
                        showingAddPropertySheet = true
                    }) {
                        HStack(spacing: 12) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(SenchiColors.senchiBlue)
                                .font(.headline)
                            Text("Add New Property")
                                .foregroundColor(SenchiColors.senchiBlue)
                                .font(.headline)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Select Property")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .sheet(isPresented: $showingAddPropertySheet) {
                AddPropertyView(
                    propertyName: $newPropertyName,
                    onAddProperty: { propertyName in
                        Task {
                            do {
                                let _ = try await addProperty(
                                    userId: userSettings.userInfo?.user_id ?? "",
                                    propertyName: propertyName,
                                    authManager: authManager
                                )
                                // Refresh properties list
                                loadProperties()
                                showingAddPropertySheet = false
                                newPropertyName = ""
                            } catch {
                                print("❌ Failed to add property: \(error)")
                            }
                        }
                    }
                )
            }
            .onAppear {
                loadProperties()
            }
        }
    }
}

struct AddPropertyView: View {
    @Binding var propertyName: String
    let onAddProperty: (String) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Property Name")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    TextField("Enter property name", text: $propertyName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .disableAutocorrection(true)
                    
                    if let error = errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }
                .padding(.horizontal)
                
                Spacer()
                
                Button(action: {
                    guard !propertyName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                        errorMessage = "Property name cannot be empty"
                        return
                    }
                    
                    isLoading = true
                    errorMessage = nil
                    
                    onAddProperty(propertyName.trimmingCharacters(in: .whitespacesAndNewlines))
                }) {
                    HStack {
                        if isLoading {
                            ProgressView()
                                .scaleEffect(0.8)
                                .foregroundColor(.white)
                        }
                        Text(isLoading ? "Adding..." : "Add Property")
                            .fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(propertyName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.gray : SenchiColors.senchiBlue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .disabled(propertyName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)
                .padding(.horizontal)
                .padding(.bottom, 20)
            }
            .navigationTitle("Add New Property")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct PropertyRowView: View {
    let property: String
    let isSelected: Bool
    let onSelect: () -> Void
    
    private func formatPropertyName(_ propertyName: String) -> String {
        return propertyName.replacingOccurrences(of: "_", with: " ")
            .split(separator: " ")
            .map { $0.capitalized }
            .joined(separator: " ")
    }
    
    var body: some View {
        Button(action: onSelect) {
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(formatPropertyName(property))
                        .font(.headline)
                        .foregroundColor(.primary)
                    Text("Property description")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                if isSelected {
                    Image(systemName: "checkmark")
                        .foregroundColor(SenchiColors.senchiBlue)
                        .font(.headline)
                }
            }
            .padding(.vertical, 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

