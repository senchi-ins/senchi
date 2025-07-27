# TODO: Delete this or the file on the iot branch

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging
from typing import Any, Optional

DATABASE_URL = os.getenv('DATABASE_URL')

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True

    def close(self):
        self.conn.close()

    def execute_with_return(self, query, params=None) -> Any:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute(query, params)
                return cur.fetchone()
            except Exception as e:
                logging.error(f"Error executing query: {e}")
    
    def execute_query(self, query, params=None) -> bool:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute(query, params)
                return True
            except Exception as e:
                logging.error(f"Error executing query: {e}")
                return False
    
    def execute_insert(self, query, params=None) -> bool:
        with self.conn.cursor() as cur:
            try:
                cur.execute(query, params)
                return True
            except Exception as e:
                logging.error(f"Error executing insert: {e}")
                return False
        
    def insert_survey_response(self, survey_response: dict):
        """Insert a survey response"""
        query = """
        INSERT INTO survey_responses (survey_id, user_id, response)
        VALUES (%s, %s, %s)
        """
        return self.execute_insert(query, (survey_response['survey_id'], survey_response['user_id'], survey_response['response']))
    
    def upsert_device_mapping(self, device_serial: str, ieee_address: str, friendly_name: str = None, 
                             device_type: str = None, model: str = None, manufacturer: str = None):
        """Insert or update device mapping"""
        query = """
        INSERT INTO device_mappings (device_serial, ieee_address, friendly_name, device_type, model, manufacturer, last_seen)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (device_serial, ieee_address) 
        DO UPDATE SET 
            friendly_name = EXCLUDED.friendly_name,
            device_type = EXCLUDED.device_type,
            model = EXCLUDED.model,
            manufacturer = EXCLUDED.manufacturer,
            last_seen = EXCLUDED.last_seen
        """
        params = (device_serial, ieee_address, friendly_name, device_type, model, manufacturer, datetime.now())
        return self.execute_insert(query, params)
    
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

    def insert_assessment_response(self, user_id: str, response: dict) -> bool:
        """
        Insert an assessment response for a user.
        """
        query = """
        INSERT INTO assessment_responses (user_id, response, created_at)
        VALUES (%s, %s, NOW())
        """
        resp = psycopg2.extras.Json(response)
        return self.execute_insert(query, (user_id, resp))

    def insert_user(
            self, 
            email: str, 
            password_hash: str, 
            full_name: str, 
            user_type: str = 'individual', 
            is_active: bool = True,
        ) -> bool:
        """
        Insert a new user into the users table.
        """
        query = """
        INSERT INTO zb_users (email, password_hash, full_name, user_type, is_active)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        params = (email, password_hash, full_name, user_type, is_active)
        return self.execute_with_return(query, params)
    
    def insert_user_property(
            self,
            property_name: str,
            address: str = None,
            property_type: str = 'residential',
            description: str = None,
            timezone: str = 'UTC',
            is_active: bool = True,
        ) -> bool:
        """
        Insert a new property into the properties table.
        """
        query = """
        INSERT INTO zb_properties (name, address, property_type, description, timezone, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (property_name, address, property_type, description, timezone, is_active)
        return self.execute_insert(query, params)
    
    def insert_user_property_relationship(
            self,
            user_id: str,
            property_id: str,
            added_by: str,
            role: str = 'owner', # TODO: Update this later?
        ) -> bool:
        """
        Insert a new user-property relationship into the user_properties table.
        """
        query = """
        INSERT INTO zb_user_properties (user_id, property_id, role, added_by)
        VALUES (%s, %s, %s, %s)
        """
        params = (user_id, property_id, role, added_by)
        return self.execute_insert(query, params)

    def insert_user_device(
            self, 
            user_id: str, 
            device_serial: str,
            property_id: str,
            device_name: str = None,
            location_description: str = None,
            wifi_ssid: str = None,
            device_status: str = 'active',
            firmware_version: str = "0.0.1",
            last_seen: datetime = datetime.now(),
        ) -> bool:
        """
        Insert a new user-device relationship into the zb_devices table.
        """
        query = """
        INSERT INTO zb_devices (
            owner_user_id, serial_number, device_name, property_id, location_description, wifi_ssid, device_status, firmware_version, last_seen
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING owner_user_id
        """
        params = (
            user_id, device_serial, device_name, property_id, location_description, wifi_ssid, device_status, firmware_version, last_seen
        )
        return self.execute_with_return(query, params)

    def insert_property(
            self,
            name: str,
            address: str = None,
            property_type: str = 'residential',
            description: str = None,
            timezone: str = 'UTC',
            is_active: bool = True,
        ) -> bool:
        """
        Insert a new property into the properties table.
        """
        query = """
        INSERT INTO zb_properties (name, address, property_type, description, timezone, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, address, property_type, description, timezone, is_active)
        return self.execute_insert(query, params)

    def insert_user_property(
            self,
            user_id: str,
            property_id: str,
            role: str = 'manager', # TODO: Update this later?
            added_by: str = None,
        ) -> bool:
        """
        Insert a new user-property relationship into the user_properties table.
        """
        query = """
        INSERT INTO zb_user_properties (user_id, property_id, role, added_by)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, property_id) DO NOTHING
        """
        params = (user_id, property_id, role, added_by)
        return self.execute_insert(query, params)

    def insert_device(
            self,
            serial_number: str,
            owner_user_id: str,
            device_name: str = None,
            property_id: str = None,
            location_description: str = None,
            wifi_ssid: str = None,
            device_status: str = 'inactive',
            firmware_version: str = None,
            last_seen: datetime = None,
        ) -> bool:
        """
        Insert a new device into the devices table.
        """
        query = """
        INSERT INTO zb_devices (
            serial_number, device_name, owner_user_id, property_id, location_description, wifi_ssid, device_status, firmware_version, last_seen
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            serial_number, device_name, owner_user_id, property_id, location_description, wifi_ssid, device_status, firmware_version, last_seen
        )
        return self.execute_insert(query, params)
    
    # Get methods
    def get_hashed_password(self, email: str) -> Optional[tuple[str, str]]:
        query = """
        SELECT id, full_name, password_hash FROM zb_users WHERE email = %s
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (email,))
            result = cur.fetchone()
            if result:
                first_name, _ = result['full_name'].split(' ', 1)
                return (result['id'], first_name, result['password_hash'])
            return None
