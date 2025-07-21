import SwiftUI
import PhotosUI
import AVFoundation
import Photos

struct External: View {
    @EnvironmentObject var userSettings: UserSettings
    @State private var answers: [UUID: SurveyAnswer] = [:]
    @State private var showSubmitAlert = false
    @State private var currentQuestionIndex = 0
    @State private var showImagePicker: Bool = false
    @State private var imagePickerSource: UIImagePickerController.SourceType = .photoLibrary
    @State private var imagePickerQuestionID: UUID? = nil
    @State private var address: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var isSubmitting: Bool = false
    @State private var submissionResult: AssessmentResponse? = nil
    @State private var showingResults: Bool = false
    
    var body: some View {
        if showingResults, let result = submissionResult {
            AssessmentResultsView(result: result) {
                // Reset survey state and go back to address input
                userSettings.survey = nil
                answers = [:]
                currentQuestionIndex = 0
                submissionResult = nil
                showingResults = false
            }
        } else {
            VStack(spacing: 0) {
                // Address input and fetch button (only if survey not loaded)
                if userSettings.survey == nil {
                    VStack(alignment: .leading, spacing: 16) {
                        // Title and subtitle
                        VStack(alignment: .leading, spacing: 4) {
                            HStack(spacing: 6) {
                                Image(systemName: "location.fill")
                                    .foregroundColor(SenchiColors.senchiBlue)
                                Text("Enter Your Address")
                                    .font(.headline)
                            }
                            Text("We'll use this to provide location-specific risk factors and recommendations")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                        // Property Address label and text field
                        VStack(alignment: .leading, spacing: 6) {
                            Text("Property Address")
                                .font(.caption)
                                .foregroundColor(.gray)
                            TextField("123 Main Street, City, Province", text: $address)
                                .textFieldStyle(PlainTextFieldStyle())
                                .padding(10)
                                .background(Color(.systemGray6))
                                .cornerRadius(8)
                        }
                        // Buttons
                        HStack(spacing: 12) {
                            // TODO: Add option to use current location instead
                            Button(action: { fetchSurvey() }) {
                                Text("Validate Address")
                                    .fontWeight(.semibold)
                                    .frame(maxWidth: .infinity)
                            }
                            .padding(.vertical, 10)
                            .background(SenchiColors.senchiBlue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                            .disabled(address.trimmingCharacters(in: .whitespaces).isEmpty || isLoading)
                        }
                        .frame(maxWidth: .infinity)
                        // Privacy & Security note
                        HStack(alignment: .top, spacing: 8) {
                            Image(systemName: "info.circle.fill")
                                .foregroundColor(SenchiColors.senchiBlue)
                                .font(.system(size: 16))
                                .padding(.top, 2)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Privacy & Security")
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                Text("Your address is used only for risk assessment and is stored securely on your device. We don't share location data with third parties.")
                                    .font(.caption2)
                                    .foregroundColor(SenchiColors.senchiBlue)
                            }
                        }
                        .padding(10)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                        if isLoading {
                            ProgressView("Loading survey...")
                                .padding(.horizontal)
                        }
                        if let error = errorMessage {
                            Text(error)
                                .foregroundColor(.red)
                                .font(.caption)
                                .padding(.horizontal)
                        }
                    }
                    .padding(20)
                    .background(Color.white)
                    .cornerRadius(16)
                    .shadow(color: Color(.black).opacity(0.06), radius: 8, x: 0, y: 2)
                    .padding(.horizontal)
                    .padding(.top, 32)
                    Spacer().frame(height: 12)
                }
                
                // Progress bar and title
                if let survey = userSettings.survey, !survey.questions.isEmpty {
                    VStack(spacing: 8) {
                        HStack {
                            VStack(alignment: .leading, spacing: 2) {
                                Text("External Risk Assessment")
                                    .font(.title2).bold()
                                Text("Help us assess your home's external risk factors")
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                            }
                            Spacer()
                        }
                        .padding(.horizontal)
                        .padding(.vertical, 4)
                        VStack(spacing: 4) {
                            ProgressView(value: Double(currentQuestionIndex + 1), total: Double(survey.questions.count))
                                .frame(maxWidth: .infinity)
                                .tint(SenchiColors.senchiBlue)
                            Text("Question \(currentQuestionIndex + 1) of \(survey.questions.count)")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.horizontal)
                        .padding(.vertical, 10)
                    }
                    // Card
                    let q = survey.questions[currentQuestionIndex]
                    VStack(alignment: .leading, spacing: 16) {
                        // Risk and priority pills
                        HStack(spacing: 8) {
                            Pill(text: q.risk_type, color: SenchiColors.senchiBlue)
                            Pill(text: q.importance, color: q.importance.contains("High") ? SenchiColors.senchiRed : .gray)
                            Pill(text: q.risk_level, color: .gray)
                        }
                        // Question
                        Text(q.question)
                            .font(.body)
                            .padding(.vertical, 4)
                        // Answer buttons
                        VStack(spacing: 8) {
                            let orderedKeys = ["Yes", "No", "N/A"] + q.rubric.keys.filter { !["Yes", "No", "N/A"].contains($0) }.sorted()
                            ForEach(orderedKeys.filter { q.rubric.keys.contains($0) }, id: \.self) { key in
                                Button(action: {
                                    answers[q.id, default: SurveyAnswer()].answer = key
                                }) {
                                    HStack {
                                        Image(systemName: answers[q.id]?.answer == key ? "checkmark.circle.fill" : "circle")
                                        Text(key)
                                            .fontWeight(.semibold)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(answers[q.id]?.answer == key ? SenchiColors.senchiBlue : Color.gray.opacity(0.1))
                                    .foregroundColor(answers[q.id]?.answer == key ? .white : .primary)
                                    .cornerRadius(8)
                                }
                            }
                        }
                        // Photo support
                        if q.requires_photo {
                            VStack(alignment: .leading, spacing: 8) {
                                if let img = answers[q.id]?.photo {
                                    Image(uiImage: img)
                                        .resizable()
                                        .scaledToFit()
                                        .frame(height: 120)
                                        .cornerRadius(10)
                                    Button("Replace Photo") {
                                        imagePickerQuestionID = q.id
                                        showImagePicker = true
                                    }
                                    .padding(.top, 4)
                                } else {
                                    HStack(spacing: 16) {
                                        Button(action: {
                                            requestCameraAccess(questionID: q.id)
                                        }) {
                                            Label("Take Photo", systemImage: "camera")
                                                .foregroundColor(SenchiColors.senchiBlue)
                                        }
                                        .disabled(!UIImagePickerController.isSourceTypeAvailable(.camera))
                                        Button(action: {
                                            requestPhotoLibraryAccess(questionID: q.id)
                                        }) {
                                            Label("Upload Photo", systemImage: "photo")
                                                .foregroundColor(SenchiColors.senchiBlue)
                                        }
                                    }
                                }
                            }
                            .padding(.top, 8)
                        }
                        // Navigation
                        HStack {
                            Button("Previous") {
                                if currentQuestionIndex > 0 { currentQuestionIndex -= 1 }
                            }
                            .disabled(currentQuestionIndex == 0)
                            .padding()
                            .background(Color.gray.opacity(0.2))
                            .foregroundColor(SenchiColors.senchiBlack)
                            .cornerRadius(8)
                            Spacer()
                            Button(currentQuestionIndex == (survey.questions.count - 1) ? "Submit" : "Next") {
                                if currentQuestionIndex < survey.questions.count - 1 {
                                    currentQuestionIndex += 1
                                } else {
                                    submitSurvey()
                                }
                            }
                            .disabled(answers[q.id]?.answer == nil)
                            .padding()
                            .background((answers[q.id]?.answer == nil) ? Color.gray.opacity(0.2) : SenchiColors.senchiBlue)
                            .foregroundColor((answers[q.id]?.answer == nil) ? SenchiColors.senchiBlack : .white)
                            .cornerRadius(8)
                        }
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(16)
                    .shadow(radius: 2)
                    .padding(.horizontal)
                    .alert(isPresented: $showSubmitAlert) {
                        if let result = submissionResult {
                            Alert(
                                title: Text("Assessment Complete"),
                                message: Text("Total Score: \(result.total_score)\nPoints Earned: \(result.points_earned)/\(result.points_possible)"),
                                dismissButton: .default(Text("OK")) {
                                    // Reset survey state
                                    userSettings.survey = nil
                                    answers = [:]
                                    currentQuestionIndex = 0
                                    submissionResult = nil
                                }
                            )
                        } else {
                            Alert(
                                title: Text("Survey Submitted"),
                                message: Text("Your answers have been saved locally."),
                                dismissButton: .default(Text("OK"))
                            )
                        }
                    }
                }
                Spacer()
                // Assessment tips
                VStack(alignment: .leading, spacing: 4) {
                    Text("Assessment Tips")
                        .font(.headline)
                        .foregroundColor(SenchiColors.senchiBlue)
                    Text("Answer honestly for the most accurate risk assessment. Photos help our experts provide better recommendations.")
                        .font(.caption)
                        .foregroundColor(SenchiColors.senchiBlack)
                }
                .padding()
                .background(Color.gray.opacity(0.08))
                .cornerRadius(12)
                .padding(.horizontal)
                .padding(.bottom, 16)
            }
            .background(Color(.white).ignoresSafeArea())
            .sheet(isPresented: $showImagePicker) {
                if let qid = imagePickerQuestionID {
                    ImagePicker(sourceType: imagePickerSource) { img in
                        if let img = img {
                            answers[qid, default: SurveyAnswer()].photo = img
                        }
                    }
                }
            }
        }
    }
    
    // FIXED: Separated permission methods for better debugging
    private func requestCameraAccess(questionID: UUID) {
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        print("Camera status: \(status.rawValue)")
        
        switch status {
        case .authorized:
            showCamera(questionID: questionID)
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async {
                    print("Camera permission granted: \(granted)")
                    if granted {
                        showCamera(questionID: questionID)
                    }
                }
            }
        case .denied, .restricted:
            print("Camera access denied or restricted")
            // You might want to show an alert here directing user to Settings
        @unknown default:
            break
        }
    }
    
    private func requestPhotoLibraryAccess(questionID: UUID) {
        let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)
        print("Photo library status: \(status.rawValue)")
        
        switch status {
        case .authorized, .limited:
            showPhotoLibrary(questionID: questionID)
        case .notDetermined:
            PHPhotoLibrary.requestAuthorization(for: .readWrite) { newStatus in
                DispatchQueue.main.async {
                    print("Photo library permission: \(newStatus.rawValue)")
                    if newStatus == .authorized || newStatus == .limited {
                        showPhotoLibrary(questionID: questionID)
                    }
                }
            }
        case .denied, .restricted:
            print("Photo library access denied or restricted")
            // You might want to show an alert here directing user to Settings
        @unknown default:
            break
        }
    }
    
    private func showCamera(questionID: UUID) {
        print("Showing camera for question: \(questionID)")
        imagePickerSource = .camera
        imagePickerQuestionID = questionID
        showImagePicker = true
    }
    
    private func showPhotoLibrary(questionID: UUID) {
        print("Showing photo library for question: \(questionID)")
        imagePickerSource = .photoLibrary
        imagePickerQuestionID = questionID
        showImagePicker = true
    }

    private func fetchSurvey() {
        isLoading = true
        errorMessage = nil
        let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/external/survey")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body = ["address": address]
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        } catch {
            errorMessage = "Failed to encode address."
            isLoading = false
            return
        }
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                if let error = error {
                    errorMessage = "Network error: \(error.localizedDescription)"
                    return
                }
                guard let data = data else {
                    errorMessage = "No data received from server."
                    return
                }
                if let string = String(data: data, encoding: .utf8) {
                    print("Raw response:\n\(string)")
                } else {
                    print("Raw response could not be decoded as UTF-8 string. Data length: \(data.count) bytes")
                }
                if let httpResponse = response as? HTTPURLResponse {
                    print("Content-Type: \(httpResponse.value(forHTTPHeaderField: "Content-Type") ?? "nil")")
                    print("Status code: \(httpResponse.statusCode)")
                }
                do {
                    let decoded = try JSONDecoder().decode(LocationRiskResponse.self, from: data)
                    userSettings.survey = Survey(locationRisks: decoded.location_risks, questions: decoded.questions)
                    self.currentQuestionIndex = 0
                } catch {
                    errorMessage = "Failed to decode survey: \(error.localizedDescription)"
                }
            }
        }.resume()
    }

    private func submitSurvey() {
        guard let survey = userSettings.survey else { return }
        
        isSubmitting = true
        errorMessage = nil
        
        // Collect all answers
        var userAnswers: [UserAnswer] = []
        for question in survey.questions {
            if let answer = answers[question.id]?.answer {
                userAnswers.append(UserAnswer(
                    question: question.question,
                    answer: answer,
                    photos: [] // Ignoring photos for now
                ))
            }
        }
        
        // Submit to backend
        let url = URL(string: "\(ApplicationConfig.restAPIBase)/api/v1/external/submit/\(UUID().uuidString)")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONEncoder().encode(userAnswers)
        } catch {
            errorMessage = "Failed to encode answers: \(error.localizedDescription)"
            isSubmitting = false
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isSubmitting = false
                
                if let error = error {
                    errorMessage = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received from server."
                    return
                }
                
                do {
                    let result = try JSONDecoder().decode(AssessmentResponse.self, from: data)
                    submissionResult = result
                    showSubmitAlert = true
                } catch {
                    errorMessage = "Failed to decode response: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

struct AssessmentResultsView: View {
    let result: AssessmentResponse
    let onGetRecommendations: () -> Void
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(SenchiColors.senchiBlue)
                    Text("Assessment Complete!")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Here's your comprehensive risk analysis")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                .padding(.top, 20)
                
                // Score Card
                // TODO truncate this
                VStack(spacing: 12) {
                    Text("Overall Risk Protection Score")
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Text("\(Int(result.total_score))%")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(.orange)
                    
                    Text("\(Int(result.points_earned)) out of \(Int(result.points_possible)) points earned")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    
                    ProgressView(value: result.total_score, total: 100)
                        .progressViewStyle(LinearProgressViewStyle(tint: SenchiColors.senchiBlue))
                        .scaleEffect(y: 2)
                    
                    HStack {
                        Image(systemName: "target")
                            .foregroundColor(.orange)
                        Text("Good Protection")
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                }
                .padding(20)
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                .cornerRadius(16)
                .padding(.horizontal)
                
                // Risk Level Breakdown
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Image(systemName: "chart.bar.fill")
                            .foregroundColor(SenchiColors.senchiBlue)
                        Text("Risk Level Breakdown")
                            .font(.headline)
                            .fontWeight(.semibold)
                    }
                    
                    Text("Performance across different risk severity levels")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    
                    VStack(spacing: 8) {
                        RiskLevelRow(level: "Very High", percentage: 0, color: .red)
                        RiskLevelRow(level: "High", percentage: 25, color: .orange)
                        RiskLevelRow(level: "Medium", percentage: 60, color: .yellow)
                        RiskLevelRow(level: "Low", percentage: 15, color: .green)
                    }
                }
                .padding(20)
                .background(RoundedRectangle(cornerRadius: 14).stroke(Color.gray.opacity(0.15)))
                .cornerRadius(16)
                .padding(.horizontal)
                
                // Areas Needing Attention
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.orange)
                        Text("Areas Needing Attention")
                            .font(.headline)
                            .fontWeight(.semibold)
                    }
                    
                    Text("Specific improvements identified for your property")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Flooding Risk")
                            .font(.subheadline)
                            .fontWeight(.semibold)
                        
                        ForEach(result.recommendations.prefix(3), id: \.question) { recommendation in
                            HStack {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .foregroundColor(.orange)
                                    .font(.caption)
                                
                                VStack(alignment: .leading, spacing: 4) {
                                    HStack {
                                        Pill(text: recommendation.risk_level, color: .red)
                                        Pill(text: recommendation.importance, color: .gray)
                                        Spacer()
                                        Text("\(Int(recommendation.points_earned))/\(Int(recommendation.points_possible)) pts")
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                    }
                                    
                                    Text(recommendation.question)
                                        .font(.caption)
                                        .multilineTextAlignment(.leading)
                                    
                                    Text("Your answer: \(recommendation.answer)")
                                        .font(.caption2)
                                        .foregroundColor(.gray)
                                }
                            }
                            .padding(12)
                            .background(Color.white)
                            .cornerRadius(8)
                        }
                    }
                }
                .padding(20)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(16)
                .padding(.horizontal)
                
                // Action Button
                Button(action: onGetRecommendations) {
                    HStack {
                        Text("View detailed recommendations")
                        Image(systemName: "arrow.right")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(SenchiColors.senchiBlue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .padding(.horizontal)
                .padding(.bottom, 20)
            }
        }
        .background(Color.white)
    }
}

struct RiskLevelRow: View {
    let level: String
    let percentage: Int
    let color: Color
    
    var body: some View {
        HStack {
            Pill(text: level, color: color)
            Text("Risk Level")
                .font(.caption)
            Spacer()
            ProgressView(value: Double(percentage), total: 100)
                .progressViewStyle(LinearProgressViewStyle(tint: color))
                .frame(width: 100)
            Text("\(percentage)%")
                .font(.caption)
                .foregroundColor(.gray)
        }
    }
}

// FIXED ImagePicker - Key changes here
struct ImagePicker: UIViewControllerRepresentable {
    var sourceType: UIImagePickerController.SourceType = .photoLibrary
    var completion: (UIImage?) -> Void
    
    @Environment(\.dismiss) private var dismiss
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        print("Creating UIImagePickerController with source type: \(sourceType.rawValue)")
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = sourceType
        
        // FIXED: Add these properties for better compatibility
        if sourceType == .camera {
            picker.cameraCaptureMode = .photo
            picker.cameraDevice = .rear
        }
        
        // FIXED: Ensure picker allows editing if needed
        picker.allowsEditing = false
        
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {
        // No updates needed
    }
    
    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        let parent: ImagePicker
        
        init(_ parent: ImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            print("Image picker finished with info: \(info.keys)")
            
            // FIXED: Try both edited and original image
            var selectedImage: UIImage?
            if let editedImage = info[.editedImage] as? UIImage {
                selectedImage = editedImage
            } else if let originalImage = info[.originalImage] as? UIImage {
                selectedImage = originalImage
            }
            
            if let image = selectedImage {
                print("Successfully got image with size: \(image.size)")
                parent.completion(image)
            } else {
                print("Failed to get image from picker")
                parent.completion(nil)
            }
            
            picker.dismiss(animated: true)
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            print("Image picker was cancelled")
            parent.completion(nil)
            picker.dismiss(animated: true)
        }
    }
}

#Preview {
    External(
//        userSettings: .environmentObject(UserSettings())
    )
}
