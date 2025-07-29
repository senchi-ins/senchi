
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS zb_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) DEFAULT 'individual' CHECK (user_type IN ('individual', 'property_manager')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS zb_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    owner_user_id UUID NOT NULL REFERENCES zb_users(id) ON DELETE CASCADE,
    property_id UUID REFERENCES zb_properties(id) ON DELETE SET NULL,
    location_description TEXT,
    wifi_ssid VARCHAR(255),
    device_status VARCHAR(50) DEFAULT 'inactive' CHECK (device_status IN ('inactive', 'active', 'offline', 'error')),
    firmware_version VARCHAR(50),
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TODO: Add to the schema after implementing role specific views
-- CREATE TABLE user_device_access (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
--     role VARCHAR(50) DEFAULT 'viewer' CHECK (role IN ('admin', 'viewer')), -- owner role is implicit via devices.owner_user_id
--     added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     added_by UUID REFERENCES users(id), -- Who granted this access
    
--     UNIQUE(user_id, device_id)
-- );

-- TODO: Add to the schema after implementing refresh tokens
-- CREATE TABLE user_refresh_tokens (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     refresh_token_hash VARCHAR(255) NOT NULL,
--     device_serial VARCHAR(100),
--     expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     last_used TIMESTAMP WITH TIME ZONE,
--     is_revoked BOOLEAN DEFAULT false
-- );

CREATE TABLE IF NOT EXISTS zb_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    property_type VARCHAR(100) DEFAULT 'residential' CHECK (property_type IN ('residential', 'commercial', 'mixed')),
    description TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS zb_user_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES zb_users(id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES zb_properties(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'tenant' CHECK (role IN ('owner', 'manager', 'tenant', 'viewer')),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES zb_users(id),
    
    UNIQUE(user_id, property_id)
);

-- CREATE TABLE device_mappings (
--     id SERIAL PRIMARY KEY,
--     device_serial UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
--     ieee_address VARCHAR(50) NOT NULL,
--     friendly_name VARCHAR(255),
--     device_type VARCHAR(100),
--     model VARCHAR(100),
--     manufacturer VARCHAR(100),
--     room VARCHAR(100), -- TODO: Add to the schema
--     floor VARCHAR(50), -- TODO: Add to the schema
--     property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     last_seen TIMESTAMP WITH TIME ZONE,
    
--     UNIQUE(device_id, ieee_address)
-- );

-- CREATE TABLE events (
--     id SERIAL PRIMARY KEY,
--     device VARCHAR(50) NOT NULL,
--     event_type VARCHAR(100) NOT NULL,
--     event_time TIMESTAMP WITH TIME ZONE NOT NULL,
--     event_location VARCHAR(100),
--     time_to_stop INTEGER,
--     event_data JSONB, -- TODO: Add to the schema
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

CREATE TABLE IF NOT EXISTS user_device_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES zb_users(id) ON DELETE CASCADE,
    device_token VARCHAR(255) NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('ios', 'android')),
    device_identifier VARCHAR(255), -- Add this: unique device ID
    device_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    
    UNIQUE(device_token)
);

-- Update existing rows
UPDATE zb_devices
SET location_id = 'rpi-zigbee-' || RIGHT(serial_number, 8)
WHERE serial_number IS NOT NULL;

-- Then make it a generated column (PostgreSQL 12+)
ALTER TABLE zb_devices
ALTER COLUMN location_id 
SET GENERATED ALWAYS AS ('rpi-zigbee-' || RIGHT(serial_number, 8)) STORED;