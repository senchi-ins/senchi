
import SwiftUI

// Ref: https://stackoverflow.com/questions/68876216/how-to-declare-global-state-variables-in-swiftui

class UserSettings: ObservableObject {
    @Published var loggedIn: Bool = true
    @Published var isOnboarded: Bool = false
    @Published var userName: String = ""
    
    // TODO: Add other variables here in the future
}
