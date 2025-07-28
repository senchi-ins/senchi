import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging

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
        SELECT ieee_address, friendly_name, device_type, model, manufacturer, device_mappings.last_seen
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
