//
//  Property.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-28.
//

import Foundation

struct PropertyRequest: Codable {
    let user_id: String
    let property_name: String?
}

struct PropertyResponse: Codable {
    let id: String
    let name: String
}
