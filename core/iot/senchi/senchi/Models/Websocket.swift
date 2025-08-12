//
//  Websocket.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

struct WebSocketMessage: Codable {
    let type: String
    let timestamp: String?
    let deviceId: String?
    let data: DeviceUpdatePayload?
    let devices: [Device]?
    
    enum CodingKeys: String, CodingKey {
        case type
        case timestamp
        case deviceId = "device_id"
        case data
        case devices
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        type = try container.decode(String.self, forKey: .type)
        timestamp = try container.decodeIfPresent(String.self, forKey: .timestamp)
        deviceId = try container.decodeIfPresent(String.self, forKey: .deviceId)
        data = try container.decodeIfPresent(DeviceUpdatePayload.self, forKey: .data)
        devices = try container.decodeIfPresent([Device].self, forKey: .devices)
    }
}
