import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging
from typing import Dict, Any, List

DATABASE_URL = os.getenv('DATABASE_URL')
logger = logging.getLogger(__name__)

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True
    
    def execute_query(self, query, params=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            result = cur.fetchall()
            return result
    
    def execute_insert(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount
    
    def upsert_device_mapping(self, device_serial: str, ieee_address: str, friendly_name: str = None, 
                             device_type: str = None, model: str = None, manufacturer: str = None):
        """Insert or update device mapping"""
        try:
            # First try to insert
            insert_query = """
            INSERT INTO device_mappings (device_serial, ieee_address, friendly_name, device_type, model, manufacturer, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Convert datetime to string for last_seen since it's text in the database
            last_seen_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            params = (device_serial, ieee_address, friendly_name, device_type, model, manufacturer, last_seen_str)
            result = self.execute_insert(insert_query, params)
            
            if result > 0:
                logger.info(f"Inserted new device mapping: {device_serial} -> {ieee_address}")
            else:
                logger.warning(f"Failed to insert device mapping: {device_serial} -> {ieee_address}")
                
        except psycopg2.IntegrityError as e:
            # If insert fails due to unique constraint on ieee_address, try to update
            if "duplicate key value violates unique constraint" in str(e):
                logger.info(f"Device mapping already exists, updating: {device_serial} -> {ieee_address}")
                update_query = """
                UPDATE device_mappings 
                SET device_serial = %s, friendly_name = %s, device_type = %s, model = %s, manufacturer = %s, last_seen = %s
                WHERE ieee_address = %s
                """
                last_seen_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_params = (device_serial, friendly_name, device_type, model, manufacturer, last_seen_str, ieee_address)
                result = self.execute_insert(update_query, update_params)
                logger.info(f"Updated device mapping: {result} rows affected")
            else:
                raise e
    
    def get_devices_by_serial(self, device_serial: str):
        """Get all devices for a given device serial"""
        query = """
        SELECT ieee_address, friendly_name, device_type, model, manufacturer, last_seen
        FROM device_mappings 
        WHERE device_serial = %s
        ORDER BY last_seen DESC
        """
        return self.execute_query(query, (device_serial,))
    
    def remove_device_mapping(self, device_serial: str, ieee_address: str):
        """Remove a device mapping"""
        query = """
        DELETE FROM device_mappings 
        WHERE device_serial = %s AND ieee_address = %s
        """
        return self.execute_insert(query, (device_serial, ieee_address))
    
    def get_user_devices(self, user_id: str, property_name: str = "main"):
        """Get all devices for a given user_id"""
        # TODO: Add property_id to the query
        query = """
        SELECT distinct(ieee_address), friendly_name, device_type, model, manufacturer, device_mappings.last_seen
        FROM zb_users JOIN zb_devices ON zb_users.id = zb_devices.owner_user_id
        JOIN device_mappings ON zb_devices.serial_number = device_mappings.device_serial
        JOIN zb_properties ON zb_properties.id = zb_devices.property_id
        JOIN zb_user_properties ON zb_user_properties.user_id = zb_users.id
        WHERE zb_users.id = %s AND zb_properties.name = %s
        ORDER BY last_seen DESC
        """
        return self.execute_query(query, (user_id, property_name))
    
    def get_device_serials(self):
        """Get all device serials for a given user_id"""
        query = """
        SELECT serial_number
        FROM zb_devices
        """
        return self.execute_query(query)
    
    def register_device_token(self, user_id: str, device_token: str, platform: str, 
                             device_identifier: str, device_info: Dict[str, Any] = None) -> str:
        """Register or update a device token for a user"""
        try:
            # First, deactivate any old tokens for this device
            deactivate_query = """
            UPDATE user_device_tokens 
            SET is_active = false, updated_at = NOW()
            WHERE user_id = %s 
            AND device_identifier = %s 
            AND platform = %s
            AND device_token != %s
            AND is_active = true
            """
            self.execute_insert(deactivate_query, (user_id, device_identifier, platform, device_token))
            
            # Convert device_info to JSON string if provided
            device_info_json = json.dumps(device_info) if device_info else None
            
            # Try to insert new token
            insert_query = """
            INSERT INTO user_device_tokens 
            (user_id, device_token, platform, device_identifier, device_info, updated_at, last_used)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
            """
            
            with self.conn.cursor() as cur:
                cur.execute(insert_query, (user_id, device_token, platform, device_identifier, device_info_json))
                result = cur.fetchone()
                if result:
                    logger.info(f"Registered new device token for user {user_id}")
                    return result[0]
                    
        except psycopg2.IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                # Token already exists, update it
                logger.info(f"Device token already exists, updating for user {user_id}")
                update_query = """
                UPDATE user_device_tokens 
                SET user_id = %s,
                    platform = %s,
                    device_identifier = %s,
                    device_info = %s,
                    updated_at = NOW(),
                    last_used = NOW(),
                    is_active = true
                WHERE device_token = %s
                RETURNING id
                """
                
                with self.conn.cursor() as cur:
                    cur.execute(update_query, (user_id, platform, device_identifier, device_info_json, device_token))
                    result = cur.fetchone()
                    if result:
                        return result[0]
            else:
                raise e
        
        except Exception as e:
            logger.error(f"Failed to register device token: {e}")
            raise e
    
    def get_user_device_tokens(self, user_id: str, platform: str = None) -> List[str]:
        """Get all active device tokens for a user"""
        base_query = """
        SELECT device_token, platform, device_info, last_used
        FROM user_device_tokens 
        WHERE user_id = %s AND is_active = true
        """
        
        if platform:
            query = base_query + " AND platform = %s ORDER BY last_used DESC"
            results = self.execute_query(query, (user_id, platform))
        else:
            query = base_query + " ORDER BY last_used DESC"
            results = self.execute_query(query, (user_id,))
        
        return [row['device_token'] for row in results] if results else []
    
    def get_user_devices_with_tokens(self, user_id: str, property_name: str = "main") -> List[Dict]:
        """Get user devices along with their push notification info"""
        query = """
        SELECT 
            dm.ieee_address,
            dm.friendly_name,
            dm.device_type,
            dm.model,
            dm.manufacturer,
            dm.last_seen,
            udt.device_token,
            udt.platform,
            udt.device_identifier,
            udt.is_active as token_active
        FROM zb_users u
        JOIN zb_devices d ON u.id = d.owner_user_id
        JOIN device_mappings dm ON d.serial_number = dm.device_serial
        JOIN zb_properties p ON p.id = d.property_id
        JOIN zb_user_properties up ON up.user_id = u.id
        LEFT JOIN user_device_tokens udt ON u.id = udt.user_id AND udt.is_active = true
        WHERE u.id = %s AND p.name = %s
        ORDER BY dm.last_seen DESC
        """
        return self.execute_query(query, (user_id, property_name))
    
    def deactivate_device_token(self, device_token: str) -> int:
        """Mark a device token as inactive (when APNs returns 410)"""
        query = """
        UPDATE user_device_tokens 
        SET is_active = false, updated_at = NOW()
        WHERE device_token = %s
        """
        result = self.execute_insert(query, (device_token,))
        if result > 0:
            logger.info(f"Deactivated device token: {device_token[:8]}...")
        return result
    
    def cleanup_old_device_tokens(self, days_old: int = 30) -> int:
        """Remove tokens that haven't been used in X days"""
        query = """
        DELETE FROM user_device_tokens 
        WHERE last_used < NOW() - INTERVAL '%s days'
        OR (is_active = false AND updated_at < NOW() - INTERVAL '7 days')
        """
        result = self.execute_insert(query % days_old)
        if result > 0:
            logger.info(f"Cleaned up {result} old device tokens")
        return result
    
    def update_token_last_used(self, device_token: str):
        """Update the last_used timestamp for a device token"""
        query = """
        UPDATE user_device_tokens 
        SET last_used = NOW()
        WHERE device_token = %s AND is_active = true
        """
        return self.execute_insert(query, (device_token,))
    
    def get_device_tokens_for_iot_device(self, device_serial: str) -> List[Dict]:
        """Get all device tokens for users who own a specific IoT device"""
        query = """
        SELECT DISTINCT 
            udt.device_token,
            udt.platform,
            u.id as user_id,
            u.full_name
        FROM zb_devices d
        JOIN zb_users u ON d.owner_user_id = u.id
        JOIN user_device_tokens udt ON u.id = udt.user_id
        JOIN device_mappings dm ON d.serial_number = dm.device_serial
        WHERE d.serial_number = %s 
        AND udt.is_active = true
        AND u.is_active = true
        """
        return self.execute_query(query, (device_serial,))
    
    def get_user_from_location_id(self, location_id: str) -> Dict:
        """Get a user from a location_id"""
        query = """
        SELECT owner_user_id, serial_number, property_id
        FROM zb_devices
        WHERE location_id = %s
        """
        return self.execute_query(query, (location_id,))
    
    # TODO: Verify this works
    def get_manager_phone_number(self, user_id: str) -> str:
        """Get a user from a location_id"""
        query = """
        SELECT manager_phone_number
        FROM zb_user_properties as u
        JOIN zb_properties as p ON u.property_id = p.id
        WHERE user_id = %s
        """
        return self.execute_query(query, (user_id,))

    def get_user_devices_by_phone(self, phone_number: str) -> List[Dict]:
        """Get all devices for a user by their phone number"""
        # TODO: Update this since user id may differ if a PM is managing multiple properties
        query = """
        SELECT 
            dm.ieee_address,
            dm.friendly_name,
            dm.device_type,
            dm.model,
            dm.manufacturer,
            dm.last_seen,
            u.id as user_id,
            d.serial_number
        FROM zb_user_properties as u
        JOIN zb_devices as d ON u.user_id = d.owner_user_id
        JOIN device_mappings as dm ON d.serial_number = dm.device_serial
        WHERE u.manager_phone_number = %s
        ORDER BY dm.last_seen DESC
        """
        return self.execute_query(query, (phone_number,))

    def update_user_phone_number(self, user_id: str, phone_number: str) -> int:
        """Update a user's phone number"""
        query = """
        UPDATE zb_users 
        SET phone_number = %s, updated_at = NOW()
        WHERE id = %s
        """
        result = self.execute_insert(query, (phone_number, user_id))
        if result > 0:
            logger.info(f"Updated phone number for user {user_id}")
        return result
    
    def get_user_from_phone_number_by_serial(self, serial_number: str, user_id: str) -> Dict:
        """Get a user from a phone number by their serial number"""
        query = """
        select distinct(manager_phone_number) 
        from zb_devices join zb_user_properties 
        ON owner_user_id = user_id 
        WHERE serial_number = %s AND user_id = %s;
        """
        return self.execute_query(query, (serial_number, user_id))
    
    def insert_alert(self, property_id: str, alert: Dict):
        """Insert an alert into the database"""
        query = """
        INSERT INTO zb_property_alerts (property_id, alert)
        VALUES (%s, %s)
        """
        return self.execute_insert(query, (property_id, alert))