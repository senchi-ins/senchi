
import SwiftUI

// Ref: https://stackoverflow.com/questions/68876216/how-to-declare-global-state-variables-in-swiftui

class UserSettings: ObservableObject {
    @Published var loggedIn: Bool = true
    @Published var isOnboarded: Bool = false
    @Published var userName: String = ""
    @Published var survey: Survey? = nil
    @Published var userInfo: UserInfoResponse? = nil
    @Published var automateResponse: Bool = false
    
    // TODO: Remove this and make API call
    // Also TODO: Make this less hacky
    @Published var homeHealthScore: Double = 0.18
}
