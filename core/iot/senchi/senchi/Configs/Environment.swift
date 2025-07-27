
import SwiftUI

// Ref: https://stackoverflow.com/questions/68876216/how-to-declare-global-state-variables-in-swiftui

class UserSettings: ObservableObject {
    @Published var loggedIn: Bool = true
    @Published var isOnboarded: Bool = false
    @Published var userName: String = ""
    @Published var survey: Survey? = nil
    
    // TODO: Add other variables here in the future
}
