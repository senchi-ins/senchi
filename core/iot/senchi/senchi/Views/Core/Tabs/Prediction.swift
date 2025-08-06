import SwiftUI
import Charts

// TODO: Base this on the actual available data
struct LeakData: Identifiable {
    let id = UUID()
    let time: Date
    let leakProbability: Double // 0.0 to 1.0
    
    static func mockData(spikeHoursFromNow: Int = 6) -> [LeakData] {
        let calendar = Calendar.current
        let now = Date()
        var data: [LeakData] = []
        
        // Calculate the spike time
        let spikeTime = calendar.date(byAdding: .hour, value: spikeHoursFromNow, to: now) ?? now
        let spikeHour = calendar.component(.hour, from: spikeTime)
        
        // Generate 24 hours of data (one data point per hour)
        for hour in 0..<24 {
            if let time = calendar.date(byAdding: .hour, value: hour, to: now) {
                // Create plateau effect - probability spikes and stays high
                let leakProbability: Double
                if hour < spikeHoursFromNow {
                    // Low probability before spike
                    leakProbability = 0.1 + Double.random(in: 0...0.1)
                } else if hour == spikeHoursFromNow {
                    // Spike at calculated time
                    leakProbability = 0.8 + Double.random(in: 0...0.15)
                } else {
                    // Plateau - stays high after spike
                    leakProbability = 0.8
                }
                data.append(LeakData(time: time, leakProbability: leakProbability))
            }
        }
        
        return data
    }
}

struct PredictionRationale {
    let rationale: String
    let icon: String
    
    static func mockData() -> [PredictionRationale] {
        // TODO:
        return [
            .init(rationale: "Decreased internal water temperature within pipe", icon: "thermometer.snowflake"),
            .init(rationale: "Local leak likely detected in upstairs bathroom", icon: "water.waves"),
        ]
    }
}

struct PreventativeActions {
    let description: String
    let icon: String
    // TODO: Upgrade function def to 
    let action: () -> Void
    
    static func mockData() -> [PreventativeActions] {
        return [
            .init(description: "Route nearest plumber", icon: "wrench.and.screwdriver") {
                // Action will be handled in the view
            },
            .init(description: "Shutoff main water valve", icon: "arrow.uturn.up.circle") {
                // Action will be handled in the view
            }
        ]
    }
}

// MARK: - Chart Component
struct LeakChartView: View {
    let leakData: [LeakData]
    let leakWindowStart: Date
    let leakWindowEnd: Date
    @Binding var selectedData: LeakData?
    @Binding var selectionPosition: CGFloat?
    @Binding var dragPosition: CGFloat?
    
    private var areaBackground: Gradient {
        return Gradient(colors: [Color(red: 0.141, green: 0.051, blue: 0.749), Color(red: 0.141, green: 0.051, blue: 0.749).opacity(0.1)])
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Selection info display
            if let selected = selectedData {
                HStack {
                    Text("\(Int(selected.leakProbability * 100))%")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(red: 0.141, green: 0.051, blue: 0.749))
                    Text("leak probability at \(selected.time, format: .dateTime.hour().minute())")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    Spacer()
                }
                .padding(.horizontal)
            }
            
            Chart(leakData) {
                // LineMark(
                //     x: .value("Time", $0.time, unit: .hour),
                //     y: .value("Probability", $0.leakProbability)
                // )
                // .symbol(.circle)
                // .symbolSize(100)
                // .interpolationMethod(.catmullRom)
                // .foregroundStyle(Color(red: 0.141, green: 0.051, blue: 0.749))
                
                AreaMark(
                    x: .value("Time", $0.time, unit: .hour),
                    y: .value("Probability", $0.leakProbability)
                )
                .interpolationMethod(.catmullRom)
                .foregroundStyle(areaBackground)
                
                // Highlight leak window with RuleMark
                // TODO: This mark should be independent of the leak start
                RuleMark(
                    xStart: .value("Start", leakWindowStart - 6, unit: .hour),
                    xEnd: .value("End", leakWindowEnd, unit: .hour)
                )
                .foregroundStyle(Color(red: 0.85, green: 0.1, blue: 0.2).opacity(0.01))
                .lineStyle(StrokeStyle(lineWidth: 2, dash: [5, 5]))
            }
            .chartXAxis {
                AxisMarks(values: .stride(by: .hour, count: 6)) { _ in
                    AxisValueLabel(format: .dateTime.hour(), centered: true)
                }
            }
            .chartYAxis {
                AxisMarks { _ in
                    // Hide y-axis marks and labels
                }
            }
            .chartYScale(domain: 0 ... 1)
            .chartOverlay { proxy in
                GeometryReader { geometry in
                    Rectangle()
                        .fill(.clear)
                        .contentShape(Rectangle())
                        .gesture(
                            DragGesture(minimumDistance: 0)
                                .onChanged { value in
                                    let plotArea = geometry[proxy.plotAreaFrame]
                                    let x = value.location.x - plotArea.origin.x
                                    
                                    // Constrain x position to chart bounds
                                    let constrainedX = max(0, min(x, plotArea.width))
                                    dragPosition = constrainedX
                                    
                                    guard let time = proxy.value(atX: constrainedX, as: Date.self) else { return }
                                    
                                    // Find the closest data point
                                    let closest = leakData.min { data1, data2 in
                                        abs(data1.time.timeIntervalSince(time)) < abs(data2.time.timeIntervalSince(time))
                                    }
                                    
                                    if let closest = closest {
                                        // Update selection with haptic feedback
                                        if selectedData?.id != closest.id {
                                            selectedData = closest
                                            selectionPosition = constrainedX
                                            
                                            // Haptic feedback
                                            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                            impactFeedback.impactOccurred()
                                        }
                                    }
                                }
                                .onEnded { _ in
                                    // Keep the final position
                                    selectionPosition = dragPosition
                                }
                        )
                }
            }
            .overlay(
                // Vertical selection line
                Group {
                    if let position = dragPosition ?? selectionPosition {
                        Rectangle()
                            .fill(Color(red: 0.141, green: 0.051, blue: 0.749).opacity(0.2))
                            .frame(width: 1.5)
                            .position(x: position, y: 150) // Center of chart
                            .animation(.easeInOut(duration: 0.1), value: position)
                    }
                }
            )
            .frame(height: 300)
        }
        .cornerRadius(16)
        .shadow(color: Color(.black).opacity(0.06), radius: 8, x: 0, y: 2)
        .padding(.vertical, 2)
    }
}

// MARK: - Leak Window Info Component
struct LeakWindowInfoView: View {
    let leakWindowStart: Date
    let leakWindowEnd: Date
    @Binding var valveShutoffCompleted: Bool
    @Binding var plumberRouted: Bool
    
    private var isLeakResolved: Bool {
        return valveShutoffCompleted && plumberRouted
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                if isLeakResolved {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(Color(red: 0.0, green: 0.7, blue: 0.3))
                } else {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(Color(red: 0.85, green: 0.1, blue: 0.2))
                }
                
                Text(isLeakResolved ? "Leak Response Complete" : "Predicted Leak Window")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(isLeakResolved ? Color(red: 0.0, green: 0.7, blue: 0.3) : Color(red: 0.85, green: 0.1, blue: 0.2))
                Spacer()
            }
            
            if isLeakResolved {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Water valve shut off and emergency plumber dispatched")
                        .font(.subheadline)
                        .foregroundColor(Color(red: 0.0, green: 0.7, blue: 0.3))
                    
                    Text("Leak threat has been contained and professional help is on the way.")
                        .font(.caption)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.leading)
                }
                .padding(.vertical, 8)
                .padding(.horizontal, 12)
                .background(Color(red: 0.0, green: 0.7, blue: 0.3).opacity(0.1))
                .cornerRadius(8)
            } else {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Start")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text(leakWindowStart, format: .dateTime.hour())
                            .font(.subheadline)
                            .fontWeight(.medium)
                    }
                    
                    Spacer()
                    
                    Image(systemName: "arrow.right")
                        .foregroundColor(.gray)
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("End")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text(leakWindowEnd, format: .dateTime.hour())
                            .font(.subheadline)
                            .fontWeight(.medium)
                    }
                }
                .padding(.vertical, 8)
                .padding(.horizontal, 12)
                .background(Color(red: 0.85, green: 0.1, blue: 0.2).opacity(0.1))
                .cornerRadius(8)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
        .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
    }
}

// MARK: - Preventative Actions Component
struct PreventativeActionsView: View {
    let automateResponse: Bool
    let onAutomationToggle: (Bool) -> Void
    @Binding var showingPlumberAlert: Bool
    @Binding var showingValveAlert: Bool
    @Binding var showingPlumberCalling: Bool
    @Binding var valveShutoffCompleted: Bool
    @Binding var plumberRouted: Bool
    
    // Animation states
    @State private var valveAnimationPlaying: Bool = false
    @State private var valveRotation: Double = 0
    @State private var valveScale: CGFloat = 1.0
    @State private var valveColor: Color = Color(red: 0.85, green: 0.1, blue: 0.2)
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "shield.checkered")
                    .foregroundColor(Color(red: 0.141, green: 0.051, blue: 0.749))
                Text("Preventative Actions")
                    .font(.headline)
                    .fontWeight(.semibold)
                Spacer()
            }
            
            // Automation Toggle
            HStack {
                Image(systemName: "bolt.fill")
                    .foregroundColor(automateResponse ? Color(red: 0.0, green: 0.7, blue: 0.3) : .gray)
                Text("Automate responses")
                    .font(.subheadline)
                    .fontWeight(.medium)
                Spacer()
                Toggle("", isOn: Binding(
                    get: { automateResponse },
                    set: { newValue in
                        onAutomationToggle(newValue)
                    }
                ))
                    .labelsHidden()
                    .onChange(of: automateResponse) { _, newValue in
                        if newValue {
                            print("Automation enabled - triggering valve shutoff")
                            // Automatically trigger valve shutoff when toggle is turned on
                            triggerValveShutoff {
                                // Show plumber calling interface after valve shutoff completes
                                print("Automation completion - setting showingPlumberCalling to true")
                                valveShutoffCompleted = true
                                plumberRouted = true
                                showingPlumberCalling = true
                            }
                        }
                    }
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background(Color.gray.opacity(0.05))
            .cornerRadius(8)
            
            // Action Buttons
            VStack(spacing: 12) {
                // Shutoff main water valve (first)
                Button(action: {
                    print("Manual valve button tapped")
                    triggerValveShutoff {
                        // Show plumber calling interface after valve shutoff completes
                        print("Manual valve completion - setting showingPlumberCalling to true")
                        showingPlumberCalling = true
                    }
                }) {
                    HStack {
                        Image(systemName: "arrow.uturn.up.circle")
                            .foregroundColor(.white)
                            .font(.system(size: 16))
                            .frame(width: 20)
                            .rotationEffect(.degrees(valveRotation))
                            .scaleEffect(valveScale)
                        
                        Text(valveAnimationPlaying ? "Shutting off..." : "Shutoff main water valve")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.white)
                        
                        Spacer()
                        
                        if valveAnimationPlaying {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(0.8)
                        } else if valveShutoffCompleted {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                                .font(.system(size: 16))
                        } else {
                            Image(systemName: "arrow.right")
                                .foregroundColor(.white.opacity(0.7))
                                .font(.system(size: 14))
                        }
                    }
                    .padding(.vertical, 12)
                    .padding(.horizontal, 16)
                    .background(valveShutoffCompleted ? .green : valveColor)
                    .cornerRadius(10)
                }
                .disabled(valveAnimationPlaying)
                
                // Route nearest plumber (second)
                Button(action: {
                    plumberRouted = true
                    showingPlumberCalling = true
                }) {
                    HStack {
                        Image(systemName: "wrench.and.screwdriver")
                            .foregroundColor(.white)
                            .font(.system(size: 16))
                            .frame(width: 20)
                        
                        Text("Route nearest plumber")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.white)
                        
                        Spacer()
                        
                        if plumberRouted {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                                .font(.system(size: 16))
                        } else {
                            Image(systemName: "arrow.right")
                                .foregroundColor(.white.opacity(0.7))
                                .font(.system(size: 14))
                        }
                    }
                    .padding(.vertical, 12)
                    .padding(.horizontal, 16)
                    .background(plumberRouted ? .green : Color(red: 0.141, green: 0.051, blue: 0.749))
                    .cornerRadius(10)
                }
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 20)
        .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
    }
    
    private func triggerValveShutoff(completion: @escaping () -> Void = {}) {
        guard !valveAnimationPlaying else { return }
        
        print("triggerValveShutoff called")
        
        // Start valve shutoff animation
        valveAnimationPlaying = true
        
        withAnimation(.easeInOut(duration: 1.5)) {
            valveRotation = -360
            valveScale = 1.2
        }
        
        // Complete the shutoff process
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            print("Valve animation completed")
            withAnimation(.easeInOut(duration: 0.5)) {
                valveScale = 1.0
                valveShutoffCompleted = true
            }
            
            valveAnimationPlaying = false
            
            // Call completion handler after valve alert
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                print("Calling completion handler")
                completion()
            }
        }
    }
}

// MARK: - Prediction Rationale Component
struct PredictionRationaleView: View {
    let predictionRationale: [PredictionRationale]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "brain.head.profile")
                    .foregroundColor(Color(red: 0.141, green: 0.051, blue: 0.749))
                Text("Prediction Factors")
                    .font(.headline)
                    .fontWeight(.semibold)
                Spacer()
            }
            
            VStack(spacing: 12) {
                ForEach(Array(predictionRationale.enumerated()), id: \.offset) { index, rationale in
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: rationale.icon)
                            .foregroundColor(Color(red: 0.141, green: 0.051, blue: 0.749))
                            .font(.system(size: 16))
                            .frame(width: 20)
                        
                        Text(rationale.rationale)
                            .font(.subheadline)
                            .foregroundColor(.black)
                            .multilineTextAlignment(.leading)
                        
                        Spacer()
                    }
                    .padding(.vertical, 8)
                    .padding(.horizontal, 12)
                    .background(Color.gray.opacity(0.05))
                    .cornerRadius(8)
                }
            }
        }
        .padding()
        .cornerRadius(16)
        .shadow(color: Color(.black).opacity(0.06), radius: 8, x: 0, y: 2)
        .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
    }
}

// MARK: - Plumber Calling Interface
struct PlumberCallingView: View {
    @Binding var isShowing: Bool
    @State private var currentStep: PlumberStep = .searching
    @State private var searchProgress: Double = 0.0
    @State private var plumberFound: Bool = false
    @State private var routeProgress: Double = 0.0
    @State private var etaMinutes: Int = 12
    
    enum PlumberStep {
        case searching, found, routing
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        isShowing = false
                    }
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.gray)
                }
                
                Spacer()
                
                Text("Emergency Plumber")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                // Placeholder for balance
                Text("")
                    .frame(width: 24)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 16)
            .background(Color.white)
            
            Divider()
            
            // Content based on current step
            ScrollView {
                VStack(spacing: 24) {
                    switch currentStep {
                    case .searching:
                        searchingView
                    case .found:
                        plumberFoundView
                    case .routing:
                        routingView
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 24)
            }
        }
        .background(Color.gray.opacity(0.05))
        .onAppear {
            startPlumberSearch()
        }
    }
    
    private var searchingView: some View {
        VStack(spacing: 24) {
            // Search animation
            VStack(spacing: 16) {
                ZStack {
                    Circle()
                        .stroke(Color(red: 0.141, green: 0.051, blue: 0.749).opacity(0.2), lineWidth: 4)
                        .frame(width: 80, height: 80)
                    
                    Circle()
                        .trim(from: 0, to: searchProgress)
                        .stroke(Color(red: 0.141, green: 0.051, blue: 0.749), style: StrokeStyle(lineWidth: 4, lineCap: .round))
                        .frame(width: 80, height: 80)
                        .rotationEffect(.degrees(-90))
                    
                    Image(systemName: "wrench.and.screwdriver")
                        .font(.title)
                        .foregroundColor(Color(red: 0.141, green: 0.051, blue: 0.749))
                }
                
                Text("Searching for nearby plumbers...")
                    .font(.headline)
                    .fontWeight(.medium)
                
                Text("Finding the best available emergency plumber in your area")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
        }
    }
    
    private var plumberFoundView: some View {
        VStack(spacing: 24) {
            // Success animation
            VStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(Color(red: 0.0, green: 0.7, blue: 0.3).opacity(0.1))
                        .frame(width: 80, height: 80)
                    
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 50))
                        .foregroundColor(Color(red: 0.0, green: 0.7, blue: 0.3))
                }
                
                Text("Plumbers Found!")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(Color(red: 0.0, green: 0.7, blue: 0.3))
                
                Text("Emergency plumbers are available")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            
            // Plumber options
            // TODO: Find and pull this in from google maps / places
            VStack(spacing: 16) {
                VStack(spacing: 16) {
                    HStack {
                        // Plumber avatar
                        ZStack {
                            Circle()
                                .fill(Color(red: 0.141, green: 0.051, blue: 0.749))
                                .frame(width: 60, height: 60)
                            
                            Text("TS")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            Text("True Service Plumbing")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            HStack(spacing: 4) {
                                Image(systemName: "star.fill")
                                    .font(.caption)
                                    .foregroundColor(.yellow)
                                Text("5.0")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                Text("(912 reviews)")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            
                            HStack(spacing: 4) {
                                Image(systemName: "clock.fill")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                Text("20 Minutes away")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        }
                        
                        Spacer()
                        
                        Button(action: {
                            // Call plumber action
                        }) {
                            Image(systemName: "phone.fill")
                                .font(.title3)
                                .foregroundColor(.white)
                                .frame(width: 44, height: 44)
                                .background(Color(red: 0.0, green: 0.7, blue: 0.3))
                                .clipShape(Circle())
                        }
                    }
                    
                    Divider()
                    
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Specialization")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text("Main waterline repair")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text("Experience")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text("7+ years")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                    }
                }
                .padding(16)
                .background(Color.white)
                .cornerRadius(12)
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
                
                VStack(spacing: 16) {
                    HStack {
                        ZStack {
                            Circle()
                                .fill(Color(red: 0.141, green: 0.051, blue: 0.749))
                                .frame(width: 60, height: 60)
                            
                            Text("SP")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Strong Plumbing Inc.")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            HStack(spacing: 4) {
                                Image(systemName: "star.fill")
                                    .font(.caption)
                                    .foregroundColor(.yellow)
                                Text("4.9")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                Text("(114 reviews)")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            
                            HStack(spacing: 4) {
                                Image(systemName: "clock.fill")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                Text("33 Minutes away")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        }
                        
                        Spacer()
                        
                        Button(action: {
                            // Call plumber action
                        }) {
                            Image(systemName: "phone.fill")
                                .font(.title3)
                                .foregroundColor(.white)
                                .frame(width: 44, height: 44)
                                .background(Color(red: 0.0, green: 0.7, blue: 0.3))
                                .clipShape(Circle())
                        }
                    }
                    
                    Divider()
                    
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Specialization")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text("Main waterline repair")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text("Experience")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text("20+ years")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                    }
                }
                .padding(16)
                .background(Color.white)
                .cornerRadius(12)
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
            }
            
            // Continue button
            Button(action: {
                withAnimation(.easeInOut(duration: 0.3)) {
                    currentStep = .routing
                }
                startRouting()
            }) {
                Text("Select & View Route")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color(red: 0.141, green: 0.051, blue: 0.749))
                    .cornerRadius(12)
            }
        }
    }
    
    private var routingView: some View {
        VStack(spacing: 24) {
            // Plumber name
            VStack(spacing: 8) {
                Text("Agent called True Service Plumbing")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.black)
                    .multilineTextAlignment(.center)
            }
            
            // ETA and distance
            VStack(spacing: 16) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Estimated Arrival")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text("\(etaMinutes) minutes")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(Color(red: 0.141, green: 0.051, blue: 0.749))
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("Distance")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text("2.3 miles")
                            .font(.subheadline)
                            .fontWeight(.medium)
                    }
                }
            }
        }
    }
    
    private func startPlumberSearch() {
        // Update search progress without animation to prevent floating
        searchProgress = 1.0
        
        // Move to found state after search completes
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
            withAnimation(.easeInOut(duration: 0.3)) {
                currentStep = .found
            }
        }
    }
    
    private func startRouting() {
        // Animate route progress
        withAnimation(.linear(duration: 5.0)) {
            routeProgress = 1.0
        }
        
        // ETA remains at initial value (no countdown)
    }
}

// MARK: - Main Prediction View
struct Prediction: View {
    let predictionRationale: [PredictionRationale]
    @EnvironmentObject var userSettings: UserSettings
    
    // Chart interaction states
    @State private var selectedData: LeakData?
    @State private var selectionPosition: CGFloat? = nil
    @State private var dragPosition: CGFloat? = nil
    
    // Preventative actions states
    @State private var showingPlumberAlert: Bool = false
    @State private var showingValveAlert: Bool = false
    
    // Plumber calling interface state
    @State private var showingPlumberCalling: Bool = false
    
    // Leak response completion states
    @State private var valveShutoffCompleted: Bool = false
    @State private var plumberRouted: Bool = false
    
    // Mock data for 24-hour leak prediction
    private var leakData: [LeakData] {
        let calendar = Calendar.current
        let now = Date()
        let spikeHoursFromNow: Double = 8 // Adjustable spike time
        
        // Check if leak response is complete
        let isLeakResolved = valveShutoffCompleted && plumberRouted
        
        return (0..<24).map { hour in
            let time = calendar.date(byAdding: .hour, value: hour, to: now) ?? now
            let hoursFromNow = Double(hour)
            
            // If leak response is complete, return low probability
            if isLeakResolved {
                // TODO: Resolve this to use the model or a more accurate baseline
                return LeakData(time: time, leakProbability: 0.05) // 5% after response
            }
            
            // Create a plateau effect with a spike
            var probability: Double = 0.1 // Base probability
            
            // Plateau effect: higher probability during certain hours (6-18)
            if hoursFromNow >= 6 && hoursFromNow <= 18 {
                probability = 0.4
            }
            
            // Spike effect around the specified time
            let distanceFromSpike = abs(hoursFromNow - spikeHoursFromNow)
            if distanceFromSpike < 3 {
                // Create a sharp spike that plateaus
                if distanceFromSpike == 0 {
                    probability = 0.9 // Peak of spike
                } else if distanceFromSpike == 1 {
                    probability = 0.85 // High plateau
                } else if distanceFromSpike == 2 {
                    probability = 0.8 // Sustained plateau
                }
            } else if hoursFromNow > spikeHoursFromNow {
                // After the spike, maintain a sustained high probability
                probability = 0.8 // Sustained high probability after spike
            }
            
            return LeakData(time: time, leakProbability: probability)
        }
    }
    
    private func updateHomeHealthScore() {
        let isLeakResolved = valveShutoffCompleted && plumberRouted
        if isLeakResolved {
            userSettings.homeHealthScore = 0.52
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Leak Prediction")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        
                        Text("AI-powered leak detection for the next 24 hours")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 20)
                    .padding(.top, 10)
                    
                    // Interactive Chart
                    LeakChartView(
                        leakData: leakData,
                        leakWindowStart: Calendar.current.date(byAdding: .hour, value: 6, to: Date()) ?? Date(),
                        leakWindowEnd: Calendar.current.date(byAdding: .hour, value: 12, to: Date()) ?? Date(),
                        selectedData: $selectedData,
                        selectionPosition: $selectionPosition,
                        dragPosition: $dragPosition
                    )
                    
                    // Leak Window Info
                    LeakWindowInfoView(
                        leakWindowStart: Calendar.current.date(byAdding: .hour, value: 6, to: Date()) ?? Date(),
                        leakWindowEnd: Calendar.current.date(byAdding: .hour, value: 12, to: Date()) ?? Date(),
                        valveShutoffCompleted: $valveShutoffCompleted,
                        plumberRouted: $plumberRouted
                    )
                    .padding(.horizontal, 20)
                    
                    // Preventative Actions
                    PreventativeActionsView(
                        automateResponse: userSettings.automateResponse,
                        onAutomationToggle: { newValue in
                            userSettings.automateResponse = newValue
                        },
                        showingPlumberAlert: $showingPlumberAlert,
                        showingValveAlert: $showingValveAlert,
                        showingPlumberCalling: $showingPlumberCalling,
                        valveShutoffCompleted: $valveShutoffCompleted,
                        plumberRouted: $plumberRouted
                    )
                    .padding(.horizontal, 20)
                    
                    // Prediction Rationale
                    PredictionRationaleView(predictionRationale: predictionRationale)
                        .padding(.horizontal, 20)
                }
                .padding(.bottom, 100) // Space for tab bar
            }
//            .background(Color.gray.opacity(0.05))
            .navigationBarHidden(true)
        }
        .alert("Plumber Alert", isPresented: $showingPlumberAlert) {
            Button("OK") { }
        } message: {
            Text("Plumber routing initiated!")
        }
        .sheet(isPresented: $showingPlumberCalling) {
            PlumberCallingView(isShowing: $showingPlumberCalling)
        }
        .onChange(of: showingPlumberCalling) { newValue in
            print("showingPlumberCalling changed to: \(newValue)")
        }
        .onChange(of: valveShutoffCompleted) { newValue in
            updateHomeHealthScore()
        }
        .onChange(of: plumberRouted) { newValue in
            updateHomeHealthScore()
        }
    }
}
