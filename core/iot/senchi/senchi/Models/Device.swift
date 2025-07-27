//
//  Device.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import Network
import UserNotifications


struct Device: Codable, Identifiable {
    let id: String
    let ieee_address: String
    let name: String?
    let friendly_name: String
    let type: String
    let manufacturer: String?
    let model_id: String?
    let power_source: String?
    let interview_completed: Bool?
    let supported: Bool?
    let disabled: Bool?
    let definition: DeviceDefinition?
    let water_leak: Bool?
    let battery: Int?
    let battery_low: Bool?
    let linkquality: Int?
    let device_temperature: Double?
    let voltage: Int?
    let power_outage_count: Int?
    let trigger_count: Int?
    let last_seen: String?
    
    enum CodingKeys: String, CodingKey {
        case ieee_address, name, friendly_name, type, manufacturer, model_id, power_source
        case interview_completed, supported, disabled, definition
        case water_leak, battery, battery_low, linkquality, device_temperature
        case voltage, power_outage_count, trigger_count, last_seen
    }
    
    // Custom initializer for creating devices with updated values
    init(
        id: String,
        ieee_address: String,
        name: String?,
        friendly_name: String,
        type: String,
        manufacturer: String?,
        model_id: String?,
        power_source: String?,
        interview_completed: Bool?,
        supported: Bool?,
        disabled: Bool?,
        definition: DeviceDefinition?,
        water_leak: Bool?,
        battery: Int?,
        battery_low: Bool?,
        linkquality: Int?,
        device_temperature: Double?,
        voltage: Int?,
        power_outage_count: Int?,
        trigger_count: Int?,
        last_seen: String?
    ) {
        self.id = id
        self.ieee_address = ieee_address
        self.name = name
        self.friendly_name = friendly_name
        self.type = type
        self.manufacturer = manufacturer
        self.model_id = model_id
        self.power_source = power_source
        self.interview_completed = interview_completed
        self.supported = supported
        self.disabled = disabled
        self.definition = definition
        self.water_leak = water_leak
        self.battery = battery
        self.battery_low = battery_low
        self.linkquality = linkquality
        self.device_temperature = device_temperature
        self.voltage = voltage
        self.power_outage_count = power_outage_count
        self.trigger_count = trigger_count
        self.last_seen = last_seen
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        ieee_address = try container.decode(String.self, forKey: .ieee_address)
        name = try container.decodeIfPresent(String.self, forKey: .name)
        friendly_name = try container.decode(String.self, forKey: .friendly_name)
        type = try container.decode(String.self, forKey: .type)
        manufacturer = try container.decodeIfPresent(String.self, forKey: .manufacturer)
        model_id = try container.decodeIfPresent(String.self, forKey: .model_id)
        power_source = try container.decodeIfPresent(String.self, forKey: .power_source)
        interview_completed = try container.decodeIfPresent(Bool.self, forKey: .interview_completed)
        supported = try container.decodeIfPresent(Bool.self, forKey: .supported)
        disabled = try container.decodeIfPresent(Bool.self, forKey: .disabled)
        definition = try container.decodeIfPresent(DeviceDefinition.self, forKey: .definition)
        water_leak = try container.decodeIfPresent(Bool.self, forKey: .water_leak)
        battery = try container.decodeIfPresent(Int.self, forKey: .battery)
        battery_low = try container.decodeIfPresent(Bool.self, forKey: .battery_low)
        linkquality = try container.decodeIfPresent(Int.self, forKey: .linkquality)
        device_temperature = try container.decodeIfPresent(Double.self, forKey: .device_temperature)
        voltage = try container.decodeIfPresent(Int.self, forKey: .voltage)
        power_outage_count = try container.decodeIfPresent(Int.self, forKey: .power_outage_count)
        trigger_count = try container.decodeIfPresent(Int.self, forKey: .trigger_count)
        last_seen = try container.decodeIfPresent(String.self, forKey: .last_seen)
        
        id = ieee_address
    }
}

struct DeviceDefinition: Codable {
    let description: String?
    let model: String?
    let vendor: String?
}

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

// TODO: Update this with additional device metrics
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
