//
//  User.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-14.
//
import SwiftUI
import Foundation


struct UserProfile: Codable {
    let id: String
    let fullName: String
    let email: String
    let createdAt: Date
}

// Users device, e.g. IPhone
struct DeviceInfo: Codable {
    let serialNumber: String
    let locationId: String
    let userId: String
    let setupDate: Date
}
