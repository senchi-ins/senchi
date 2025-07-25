import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True
    
    def execute_query(self, query, params=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()
    
    def execute_insert(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount
    
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
    
    def get_user_devices(self, user_id: str, property_name: str = "main"):
        """Get all devices for a given user_id"""
        # TODO: Add property_id to the query
        query = """
        SELECT ieee_address, friendly_name, device_type, model, manufacturer, device_mappings.last_seen
        FROM zb_users JOIN zb_devices ON zb_users.id = zb_devices.owner_user_id
        JOIN device_mappings ON zb_devices.serial_number = device_mappings.device_serial
        JOIN zb_properties ON zb_properties.id = zb_devices.property_id
        JOIN zb_user_properties ON zb_user_properties.user_id = zb_users.id
        WHERE zb_users.id = %s AND zb_properties.name = %s
        ORDER BY last_seen DESC
        """
        return self.execute_query(query, (user_id, property_name))
