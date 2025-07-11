//
//  Device.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import UIKit
import Network
import UserNotifications

struct IoTDevice: Codable {
    let id: String
    let name: String?
    var status: DeviceStatus
    var lastSeen: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case status
        case lastSeen = "last_seen"
    }
    
    init(id: String, name: String? = nil, status: DeviceStatus = DeviceStatus(), lastSeen: Date = Date()) {
        self.id = id
        self.name = name
        self.status = status
        self.lastSeen = lastSeen
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decodeIfPresent(String.self, forKey: .name)
        status = try container.decode(DeviceStatus.self, forKey: .status)
        
        if let timestampString = try container.decodeIfPresent(String.self, forKey: .lastSeen) {
            let formatter = ISO8601DateFormatter()
            lastSeen = formatter.date(from: timestampString) ?? Date()
        } else {
            lastSeen = Date()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encodeIfPresent(name, forKey: .name)
        try container.encode(status, forKey: .status)
        
        let formatter = ISO8601DateFormatter()
        try container.encode(formatter.string(from: lastSeen), forKey: .lastSeen)
    }
}

struct DeviceStatus: Codable {
    var waterLeak: Bool?
    var battery: Int?
    var batteryLow: Bool?
    var linkQuality: Int?
    var deviceTemperature: Double?
    
    enum CodingKeys: String, CodingKey {
        case waterLeak = "water_leak"
        case battery
        case batteryLow = "battery_low"
        case linkQuality = "linkquality"
        case deviceTemperature = "device_temperature"
    }
}
