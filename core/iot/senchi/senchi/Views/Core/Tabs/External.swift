import SwiftUI
import PhotosUI
import AVFoundation
import Photos

// Your existing structs remain the same...
struct SurveyQuestion: Identifiable, Codable {
    let id = UUID()
    let question: String
    let risk: [String]
    let importance: [String]
    let requires_photo: Bool
    let rubric: [String: Int]
}

struct Survey: Codable {
    let risk_questions: [SurveyQuestion]
}

struct SurveyAnswer {
    var answer: String? = nil
    var photo: UIImage? = nil
}

struct Pill: View {
    let text: String
    let color: Color
    var body: some View {
        Text(text)
            .font(.caption)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(color.opacity(0.15))
            .foregroundColor(color)
            .cornerRadius(12)
    }
}

struct External: View {
    @State private var survey: Survey? = nil
    @State private var answers: [UUID: SurveyAnswer] = [:]
    @State private var showSubmitAlert = false
    @State private var currentQuestionIndex = 0
    @State private var showImagePicker: Bool = false
    @State private var imagePickerSource: UIImagePickerController.SourceType = .photoLibrary
    @State private var imagePickerQuestionID: UUID? = nil
    
    var body: some View {
        VStack(spacing: 0) {
            // Progress bar and title
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
                VStack(spacing: 4) {
                    ProgressView(value: Double(currentQuestionIndex + 1), total: Double(survey?.risk_questions.count ?? 1))
                        .frame(maxWidth: .infinity)
                        .tint(.blue) // Changed from SenchiColors.senchiBlue
                    Text("Question \(currentQuestionIndex + 1) of \(survey?.risk_questions.count ?? 1)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity)
                .padding(.horizontal)
            }
            .padding(.top, 24)
            .padding(.bottom, 10)
            Spacer().frame(height: 12)
            
            // Card
            if let questions = survey?.risk_questions, !questions.isEmpty {
                let q = questions[currentQuestionIndex]
                VStack(alignment: .leading, spacing: 16) {
                    // Risk and priority pills
                    HStack(spacing: 8) {
                        ForEach(q.risk, id: \.self) { risk in
                            Pill(text: risk, color: .blue) // Changed from SenchiColors.senchiBlue
                        }
                        ForEach(q.importance, id: \.self) { imp in
                            Pill(text: imp, color: imp.contains("High") ? .red : .gray) // Changed from SenchiColors.senchiRed
                        }
                    }
                    
                    // Question
                    Text(q.question)
                        .font(.body)
                        .padding(.vertical, 4)
                    
                    // Answer buttons
                    VStack(spacing: 8) {
                        ForEach(Array(q.rubric.keys), id: \.self) { key in
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
                                .background(answers[q.id]?.answer == key ? .blue : Color.gray.opacity(0.1)) // Changed from SenchiColors.senchiBlue
                                .foregroundColor(answers[q.id]?.answer == key ? .white : .primary)
                                .cornerRadius(8)
                            }
                        }
                    }
                    
                    // Photo support - FIXED SECTION
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
                                    // Camera Button - FIXED
                                    Button(action: {
                                        requestCameraAccess(questionID: q.id)
                                    }) {
                                        Label("Take Photo", systemImage: "camera")
                                            .foregroundColor(.blue)
                                    }
                                    .disabled(!UIImagePickerController.isSourceTypeAvailable(.camera))
                                    
                                    // Photo Library Button - FIXED
                                    Button(action: {
                                        requestPhotoLibraryAccess(questionID: q.id)
                                    }) {
                                        Label("Upload Photo", systemImage: "photo")
                                            .foregroundColor(.blue)
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
                        .cornerRadius(8)
                        Spacer()
                        Button(currentQuestionIndex == (questions.count - 1) ? "Submit" : "Next") {
                            if currentQuestionIndex < questions.count - 1 {
                                currentQuestionIndex += 1
                            } else {
                                showSubmitAlert = true
                            }
                        }
                        .padding()
                        .background(.blue) // Changed from SenchiColors.senchiBlue
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(16)
                .shadow(radius: 2)
                .padding(.horizontal)
                .alert(isPresented: $showSubmitAlert) {
                    Alert(title: Text("Survey Submitted"), message: Text("Your answers have been saved locally."), dismissButton: .default(Text("OK")))
                }
            }
            Spacer()
            
            // Assessment tips
            VStack(alignment: .leading, spacing: 4) {
                Text("Assessment Tips")
                    .font(.headline)
                    .foregroundColor(.blue) // Changed from SenchiColors.senchiBlue
                Text("Answer honestly for the most accurate risk assessment. Photos help our experts provide better recommendations.")
                    .font(.caption)
                    .foregroundColor(.black) // Changed from SenchiColors.senchiBlack
            }
            .padding()
            .background(Color.gray.opacity(0.08))
            .cornerRadius(12)
            .padding(.horizontal)
            .padding(.bottom, 16)
        }
        .background(Color(.white).ignoresSafeArea())
        .onAppear(perform: loadSurvey)
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
    
    func loadSurvey() {
        if let url = Bundle.main.url(forResource: "survey", withExtension: "json") {
            do {
                let data = try Data(contentsOf: url)
                let decoder = JSONDecoder()
                let loaded = try decoder.decode(Survey.self, from: data)
                survey = loaded
            } catch {
                print("Failed to load survey: \(error)")
            }
        } else {
            print("survey.json not found in bundle!")
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
    External()
}
