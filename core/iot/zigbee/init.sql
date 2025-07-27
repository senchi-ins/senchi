-- Initialize database tables for Senchi Home Automation

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    device VARCHAR(255),
    event_type VARCHAR(255),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_location VARCHAR(255),
    time_to_stop INTEGER
);

-- Create device_mappings table
CREATE TABLE IF NOT EXISTS device_mappings (
    id SERIAL PRIMARY KEY,
    device_serial VARCHAR(255) NOT NULL,
    ieee_address VARCHAR(255) NOT NULL,
    friendly_name VARCHAR(255),
    device_type VARCHAR(255),
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_serial, ieee_address)
);

-- Remove unique constraint on device_serial if it exists (in case it was accidentally added)
ALTER TABLE device_mappings DROP CONSTRAINT IF EXISTS device_mappings_device_serial_key;

-- Insert the two existing leak sensors
INSERT INTO device_mappings (id, device_serial, ieee_address, friendly_name, device_type, model, manufacturer)
VALUES 
    (1, '1752620536f20e64', '0x00158d008b91088e', '0x00158d008b91088e', 'leak_sensor', 'aqara', 'aqara'),
    (2, '1752620536f20e64', '0x00158d008b91089c', '0x00158d008b91089c', 'leak_sensor', 'aqara', 'aqara')
ON CONFLICT (id) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_device ON events(device);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_event_time ON events(event_time);
CREATE INDEX IF NOT EXISTS idx_device_mappings_serial ON device_mappings(device_serial);
CREATE INDEX IF NOT EXISTS idx_device_mappings_ieee ON device_mappings(ieee_address); 