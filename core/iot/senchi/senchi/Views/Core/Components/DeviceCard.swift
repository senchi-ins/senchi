
import SwiftUI


struct DeviceCardView: View {
    enum Status { case online, warning }
    var icon: String
    var name: String
    var type: String
    var status: Status
    var time: String
    var details: [String]
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(SenchiColors.senchiBlue)
                    .frame(width: 28, height: 28)
                VStack(alignment: .leading, spacing: 2) {
                    Text(name).fontWeight(.semibold).foregroundColor(.black)
                    Text(type).font(.caption).foregroundColor(.gray)
                }
                Spacer()
                if status == .online {
                    Text("online")
                        .font(.caption2)
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.blue)
                        .cornerRadius(6)
                } else if status == .warning {
                    Text("warning")
                        .font(.caption2)
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.red)
                        .cornerRadius(6)
                }
                Text(time)
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
            ForEach(details, id: \ .self) { detail in
                if status == .warning {
                    HStack(spacing: 4) {
                        Image(systemName: "exclamationmark.triangle.fill").foregroundColor(.orange)
                        Text(detail).font(.caption).foregroundColor(.orange)
                    }
                } else {
                    Text(detail).font(.caption).foregroundColor(.black)
                }
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
        .cornerRadius(12)
        .shadow(color: Color(.black).opacity(0.03), radius: 2, x: 0, y: 1)
    }
}
