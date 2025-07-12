//
//  Config.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-07.
//
import SwiftUI


struct ApplicationConfig {
    static let wsURL: String =  "wss://senchi-mqtt.up.railway.app/ws"
    static let apiBase: String = "https://senchi-mqtt.up.railway.app"
    static let hubName: String = "HomeGuard Hub"
}

struct SenchiColors {
    static let senchiBlue = Color(red: 0.141, green: 0.051, blue: 0.749)
    static let senchiBackground = Color(red: 0.937, green: 0.933, blue: 0.906)
}
