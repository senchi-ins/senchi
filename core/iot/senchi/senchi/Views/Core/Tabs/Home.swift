
import SwiftUI

struct HomeTabContent: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Greeting
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Good morning, werwer")
                            .font(.title3).fontWeight(.semibold)
                            .foregroundColor(.black)
                        Text("Your home is protected")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    ZStack {
                        Circle().fill(SenchiColors.senchiBlue.opacity(0.08)).frame(width: 36, height: 36)
                        Image(systemName: "shield.fill")
                            .foregroundColor(SenchiColors.senchiBlue)
                    }
                }
                // Health Score
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Home Health Score")
                                .font(.caption)
                                .foregroundColor(.gray)
                            // TODO: Update to read from api
                            HStack(alignment: .center, spacing: 8) {
                                Text("85%")
                                    .font(.title2).fontWeight(.bold)
                                    .foregroundColor(SenchiColors.senchiBlue)
                                Spacer()
                                HStack(spacing: 4) {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .foregroundColor(.yellow)
                                    Text("Good")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                            }
                        }
                    }
                    ProgressView(value: 0.85)
                        .accentColor(SenchiColors.senchiBlue)
                    Text("1 alert require attention")
                        .font(.caption2)
                        .foregroundColor(.gray)
                }
                .padding()
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                // Device/Savings
                HStack(spacing: 16) {
                    VStack {
                        // TODO: Get this to read from the returned list
                        Text("4")
                            .font(.title2).fontWeight(.bold)
                            .foregroundColor(.black)
                        Text("Connected Devices")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                    VStack {
                        Text("$127")
                            .font(.title2).fontWeight(.bold)
                            .foregroundColor(.green)
                        Text("Est. Savings")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                }
                // Connected Devices
                HStack {
                    Text("Connected Devices")
                        .font(.headline)
                        .foregroundColor(.black)
                    Spacer()
                    Button(action: {}) {
                        HStack(spacing: 4) {
                            // TODO: Fix colours
                            Image(systemName: "plus.circle.fill").background(Color.white).clipShape(Circle())
                                .foregroundColor(SenchiColors.senchiBlue)
                            Text("Add Device")
                                .foregroundColor(.white)
                        }
                        .font(.subheadline)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(SenchiColors.senchiBlue)
                        .cornerRadius(8)
                    }
                }
                // TODO: Load in based on live data
                VStack(spacing: 12) {
                    // Device Cards (mocked)
                    DeviceCardView(
                        icon: "thermometer",
                        name: "Living Room Sensor",
                        type: "Temperature & Humidity",
                        status: .online,
                        time: "2 min ago",
                        details: ["Temperature: 72°F", "Humidity: 45%"]
                    )
                    DeviceCardView(
                        icon: "drop.fill",
                        name: "Kitchen Water Sensor",
                        type: "Water Leak Detection",
                        status: .online,
                        time: "5 min ago",
                        details: ["No leaks detected"]
                    )
                    DeviceCardView(
                        icon: "humidity",
                        name: "Basement Moisture",
                        type: "Humidity Monitor",
                        status: .warning,
                        time: "1 min ago",
                        details: ["High humidity detected - check ventilation"]
                    )
                    DeviceCardView(
                        icon: "bolt.fill",
                        name: "Main Circuit Monitor",
                        type: "Electrical Safety",
                        status: .online,
                        time: "3 min ago",
                        details: ["Voltage: 120V"]
                    )
                }
            }
            .padding(20)
        }
    }
}

