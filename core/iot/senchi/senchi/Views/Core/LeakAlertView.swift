import SwiftUI

struct LeakAlertView: View {
    let deviceName: String
    let location: String
    let timestamp: Date
    let onDismiss: () -> Void
    
    var body: some View {
        VStack(spacing: 24) {
            // Header
            VStack(spacing: 8) {
                ZStack {
                    Circle()
                        .fill(Color.red.opacity(0.15))
                        .frame(width: 80, height: 80)
                    Image(systemName: "drop.fill")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 40, height: 40)
                        .foregroundColor(.red)
                }
                
                Text("🚨 WATER LEAK DETECTED!")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
            }
            
            // Alert Details
            VStack(spacing: 16) {
                AlertDetailRow(
                    icon: "location.fill",
                    title: "Location",
                    value: location,
                    color: .blue
                )
                
                AlertDetailRow(
                    icon: "sensor.tag.radiowaves.forward",
                    title: "Sensor",
                    value: deviceName,
                    color: .orange
                )
                
                AlertDetailRow(
                    icon: "clock.fill",
                    title: "Detected",
                    value: timestamp.formatted(date: .abbreviated, time: .shortened),
                    color: .gray
                )
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(12)
            
            // Action Buttons
            VStack(spacing: 12) {
                Button(action: {
                    // TODO: Call emergency contact or plumber
                    print("Calling emergency contact...")
                }) {
                    HStack {
                        Image(systemName: "phone.fill")
                        Text("Call Emergency Contact")
                            .fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                
                Button(action: {
                    // TODO: Navigate to device details
                    print("Viewing device details...")
                }) {
                    HStack {
                        Image(systemName: "info.circle.fill")
                        Text("View Device Details")
                            .fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                
                Button(action: onDismiss) {
                    Text("Dismiss")
                        .fontWeight(.medium)
                        .foregroundColor(.gray)
                }
            }
            
            Spacer()
        }
        .padding(24)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color.black.opacity(0.1), radius: 20, x: 0, y: 10)
        .padding(.horizontal, 20)
    }
}

struct AlertDetailRow: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 20)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.gray)
                Text(value)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.black)
            }
            
            Spacer()
        }
    }
}

#Preview {
    LeakAlertView(
        deviceName: "Kitchen Water Sensor",
        location: "Kitchen",
        timestamp: Date(),
        onDismiss: {}
    )
} 