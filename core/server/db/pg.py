# TODO: Delete this or the file on the iot branch

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging

DATABASE_URL = os.getenv('DATABASE_URL')

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True

    def close(self):
        self.conn.close()
    
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
