
import SwiftUI

struct HealthSavings: View {
    @State private var selectedTab: Tab = .health
    enum Tab { case health, savings }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header
                VStack(alignment: .leading, spacing: 4) {
                    Text("Health & Savings")
                        .font(.title2).fontWeight(.bold).foregroundColor(.black)
                    Text("Track your home's health and insurance savings")
                        .font(.subheadline).foregroundColor(.gray)
                }
                .padding(.top, 8)
                // Tab Switcher
                HStack(spacing: 0) {
                    Button(action: { selectedTab = .health }) {
                        Text("Health")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(selectedTab == .health ? Color.white : Color.clear)
                            .padding()
                            .foregroundColor(selectedTab == .health ? SenchiColors.senchiBlue : .gray)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    Button(action: { selectedTab = .savings }) {
                        Text("Savings")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(selectedTab == .savings ? Color.white : Color.clear)
                            .foregroundColor(selectedTab == .savings ? SenchiColors.senchiBlue : .gray)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                }
                .background(Color(.systemGray6))
                .clipShape(RoundedRectangle(cornerRadius: 16))
                .padding(.vertical, 4)
                // Content
                if selectedTab == .health {
                    HealthTabContent()
                } else {
                    SavingsTabContent()
                }
            }
            .padding(20)
            .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
        }
    }
}

private struct HealthTabContent: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Overall Home Health
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Overall Home Health")
                        .font(.headline).foregroundColor(.black)
                    Text("85%")
                        .font(.largeTitle).fontWeight(.bold).foregroundColor(SenchiColors.senchiBlue)
                    Text("Good condition")
                        .font(.subheadline).foregroundColor(.gray)
                }
                Spacer()
                ZStack {
                    Circle().stroke(Color(.systemGray5), lineWidth: 8).frame(width: 60, height: 60)
                    Circle().trim(from: 0, to: 0.85).stroke(SenchiColors.senchiBlue, style: StrokeStyle(lineWidth: 8, lineCap: .round)).rotationEffect(.degrees(-90)).frame(width: 60, height: 60)
                    Text("85%")
                        .font(.headline).foregroundColor(SenchiColors.senchiBlue)
                }
            }
            HStack(spacing: 16) {
                VStack {
                    Text("88%")
                        .font(.title3).fontWeight(.bold).foregroundColor(SenchiColors.senchiBlue)
                    Text("Internal Health")
                        .font(.caption).foregroundColor(SenchiColors.senchiBlue)
                }
                .frame(maxWidth: .infinity)
                .padding(12)
                .background(Color.blue.opacity(0.08))
                .cornerRadius(12)
                VStack {
                    Text("82%")
                        .font(.title3).fontWeight(.bold).foregroundColor(SenchiColors.senchiGreen)
                    Text("External Health")
                        .font(.caption).foregroundColor(SenchiColors.senchiGreen)
                }
                .frame(maxWidth: .infinity)
                .padding(12)
                .background(Color.green.opacity(0.08))
                .cornerRadius(12)
            }
            // Internal Health
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 8) {
                    Image(systemName: "house.fill").foregroundColor(SenchiColors.senchiBlue)
                    Text("Internal Health")
                        .font(.headline).foregroundColor(.black)
                }
                HealthBarRow(label: "Air Quality", percent: 0.92)
                HealthBarRow(label: "Electrical Safety", percent: 0.95)
                HealthBarRow(label: "Water Systems", percent: 0.85)
                HealthBarRow(label: "Temperature Control", percent: 0.78)
            }
            .padding()
            .background(Color.white)
            .cornerRadius(14)
            .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
            // External Health
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 8) {
                    Image(systemName: "shield.lefthalf.fill").foregroundColor(SenchiColors.senchiGreen)
                    Text("External Health")
                        .font(.headline).foregroundColor(.black)
                }
                HealthBarRow(label: "Roof Condition", percent: 0.85)
                HealthBarRow(label: "Foundation", percent: 0.90)
                HealthBarRow(label: "Exterior Walls", percent: 0.75)
                HealthBarRow(label: "Weather Resistance", percent: 0.80)
            }
            .padding()
            .cornerRadius(14)
        }
    }
}

private struct HealthBarRow: View {
    var label: String
    var percent: Double
    var body: some View {
        HStack {
            Text(label).font(.subheadline).foregroundColor(.black)
            Spacer()
            Text("\(Int(percent * 100))%")
                .font(.subheadline).foregroundColor(SenchiColors.senchiBlue)
            ZStack(alignment: .leading) {
                Capsule().fill(Color(.systemGray5)).frame(width: 80, height: 8)
                Capsule().fill(SenchiColors.senchiBlue).frame(width: CGFloat(80 * percent), height: 8)
            }
        }
    }
}

private struct SavingsTabContent: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Insurance Savings
            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 8) {
                    Image(systemName: "dollarsign.circle.fill").foregroundColor(SenchiColors.senchiGreen)
                    Text("Insurance Savings")
                        .font(.headline).foregroundColor(SenchiColors.senchiGreen)
                }
                Text("You've saved 10% on your insurance premium")
                    .font(.subheadline).foregroundColor(.gray)
                Text("$1,542")
                    .font(.largeTitle).fontWeight(.bold).foregroundColor(SenchiColors.senchiGreen)
                Text("Total savings to date")
                    .font(.caption).foregroundColor(.gray)
                HStack(spacing: 16) {
                    VStack {
                        Text("$127")
                            .font(.title3).fontWeight(.bold).foregroundColor(SenchiColors.senchiGreen)
                        Text("This month")
                            .font(.caption).foregroundColor(SenchiColors.senchiGreen)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(12)
                    .background(Color.green.opacity(0.08))
                    .cornerRadius(12)
                    VStack {
                        Text("$1850")
                            .font(.title3).fontWeight(.bold).foregroundColor(SenchiColors.senchiBlue)
                        Text("Projected annual")
                            .font(.caption).foregroundColor(SenchiColors.senchiBlue)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(12)
                    .background(Color.blue.opacity(0.08))
                    .cornerRadius(12)
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(14)
            // Claims Prevention
            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 8) {
                    Image(systemName: "shield.fill").foregroundColor(SenchiColors.senchiBlue)
                    Text("Claims Prevention")
                        .font(.headline).foregroundColor(SenchiColors.senchiBlue)
                }
                Text("3 potential claims prevented this year")
                    .font(.subheadline).foregroundColor(.gray)
                VStack(spacing: 8) {
                    ClaimRow(title: "Water leak detected early", date: "March 15, 2024", amount: "$2,400 saved", color: .yellow)
                    ClaimRow(title: "Electrical issue prevented", date: "February 8, 2024", amount: "$1,800 saved", color: .orange)
                    ClaimRow(title: "HVAC maintenance alert", date: "January 22, 2024", amount: "$950 saved", color: .blue)
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(14)
            // Monthly Savings Trend
            VStack(alignment: .leading, spacing: 8) {
                Text("Monthly Savings Trend")
                    .font(.headline).foregroundColor(.black)
                VStack(spacing: 8) {
                    SavingsBarRow(month: "Jan", value: 98)
                    SavingsBarRow(month: "Feb", value: 112)
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(14)
        }
    }
}

private struct ClaimRow: View {
    var title: String
    var date: String
    var amount: String
    var color: Color
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(title).font(.subheadline).foregroundColor(.black)
                Text(date).font(.caption2).foregroundColor(.gray)
            }
            Spacer()
            Text(amount)
                .font(.subheadline).fontWeight(.bold).foregroundColor(color)
        }
        .padding(10)
        .background(color.opacity(0.08))
        .cornerRadius(10)
    }
}

private struct SavingsBarRow: View {
    var month: String
    var value: Int
    var body: some View {
        HStack {
            Text(month).font(.subheadline).foregroundColor(.black)
            Spacer()
            Text("$\(value)").font(.subheadline).foregroundColor(SenchiColors.senchiBlue)
            ZStack(alignment: .leading) {
                Capsule().fill(Color(.systemGray5)).frame(width: 80, height: 8)
                Capsule().fill(SenchiColors.senchiBlue).frame(width: CGFloat(value), height: 8)
            }
        }
    }
}

#Preview {
    HealthSavings()
}
