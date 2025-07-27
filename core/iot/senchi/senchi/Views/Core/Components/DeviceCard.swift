
import SwiftUI


struct DeviceCardView: View {
    let device: Device
    @State private var isAlerting = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: getDeviceIcon())
                    .foregroundColor(getIconColor())
                    .frame(width: 28, height: 28)
                VStack(alignment: .leading, spacing: 2) {
                    Text(getDeviceName()).fontWeight(.semibold).foregroundColor(.black)
                    Text("\(getDeviceType())").font(.caption).foregroundColor(.gray)
                }
                Spacer()
                
                // Connection status icon
                Image(systemName: isDeviceOnline() ? "circle.fill" : "circle")
                    .foregroundColor(isDeviceOnline() ? .green : .red)
                    .frame(width: 12, height: 12)
                
                // Functionality trigger button if available
                if hasFunctionality() {
                    Button(action: {
                        triggerFunctionality()
                    }) {
                        Image(systemName: getFunctionalityIcon())
                            .foregroundColor(.blue)
                            .frame(width: 20, height: 20)
                    }
                }
            }
            
            ForEach(getDeviceDetails(), id: \.self) { detail in
                if hasAlert() {
                    HStack(spacing: 4) {
                        Image(systemName: "exclamationmark.triangle.fill").foregroundColor(.red)
                        Text(detail).font(.caption).foregroundColor(.red)
                    }
                } else {
                    Text(detail).font(.caption).foregroundColor(.black)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 14)
                .stroke(hasAlert() ? Color.red : Color.gray.opacity(0.15), lineWidth: hasAlert() ? 2 : 1)
        )
        .cornerRadius(12)
        .scaleEffect(isAlerting ? 1.02 : 1.0)
        .animation(.easeInOut(duration: 0.5).repeatForever(autoreverses: true), value: isAlerting)
        .onAppear {
            if hasAlert() {
                isAlerting = true
            }
        }
    }
    
    private func getDeviceIcon() -> String {
        if device.model_id?.contains("wleak") == true {
            return "drop.fill"
        } else if device.model_id?.contains("sensor") == true {
            return "thermometer"
        } else {
            return "sensor"
        }
    }
    
    private func getIconColor() -> Color {
        if hasAlert() {
            return .red
        } else {
            return .blue
        }
    }
    
    private func getDeviceName() -> String {
        return device.name?.isEmpty == false ? device.name! : device.friendly_name
    }
    
    private func getDeviceType() -> String {
        let rawType = device.type
        return rawType.replacingOccurrences(of: "_", with: " ")
                      .localizedCapitalized
    }
    
    private func hasAlert() -> Bool {
        return device.water_leak == true || device.battery_low == true
    }
    
    private func isDeviceOnline() -> Bool {
        // TODO: Find better way to validate this
        return device.interview_completed == true || device.last_seen != nil
    }
    
    private func hasFunctionality() -> Bool {
        // Check if device has any controllable functionality
        // This could be expanded based on device type and capabilities
        return device.type == "Router" || device.model_id?.contains("switch") == true
    }
    
    private func getFunctionalityIcon() -> String {
        if device.model_id?.contains("switch") == true {
            return "power"
        } else {
            return "gear"
        }
    }
    
    private func triggerFunctionality() {
        // This would trigger device-specific functionality
        // For now, just print the action
        print("Triggering functionality for device: \(device.friendly_name)")
        
        // Example: Toggle switch, trigger sensor reading, etc.
        // This could be expanded to make API calls to control devices
        // TODO: Implement for shutoff valve
    }
    
    private func getDeviceDetails() -> [String] {
        var details: [String] = []
        
        if let battery = device.battery {
            details.append("Battery: \(battery)%")
        }
        
        if let waterLeak = device.water_leak {
            if waterLeak {
                details.append("🚨 WATER LEAK DETECTED!")
            } else {
                details.append("No leaks detected")
            }
        }
        
        if let batteryLow = device.battery_low, batteryLow {
            details.append("⚠️ Battery low")
        }
        
        if let linkQuality = device.linkquality {
            details.append("Signal: \(linkQuality)")
        }
        
        if let temperature = device.device_temperature {
            details.append("Temperature: \(String(format: "%.1f°C", temperature))")
        }
        
        if let voltage = device.voltage {
            details.append("Voltage: \(voltage)mV")
        }
        
        if let triggerCount = device.trigger_count {
            details.append("Triggers: \(triggerCount)")
        }
        
        if let powerOutages = device.power_outage_count {
            details.append("Power outages: \(powerOutages)")
        }
        
        // Only show connection status if no other details
        if details.isEmpty {
            details.append(isDeviceOnline() ? "" : "Disconnected")
        }
        
        return details
    }
}
