import jwt
import uuid
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import HTTPException
from maindb.pg import PostgresDB
from models.tokens import TokenResponse, NotificationPayload
from notifications.apns_service import APNsService
from cfg import NOTIFICATION_CONFIG
from sms.sms import MessageBot

logger = logging.getLogger(__name__)


class NotificationRouter:
    def __init__(self, db: PostgresDB, apns_service: APNsService):
        self.db = db
        self.apns_service = apns_service

        # TODO: Move this or use the shared instance
        self.sms_service = MessageBot()
    
    async def route_mqtt_message(self, topic: str, payload: dict):
        """Route MQTT message to correct users"""
        try:
            # Extract location from topic: zigbee2mqtt/rpi-zigbee-abc123/device/event
            topic_parts = topic.split('/')
            if len(topic_parts) < 2:
                return
            
            location_id = topic_parts[1]  # e.g., "rpi-zigbee-abc123"
            serial_number = location_id.split('-')[-1]
            
            # Get all users for this location
            # TODO: Replace with Postgres query
            user_ids = self.db.get_user_from_location_id(location_id)
            user_ids = [(user_id["owner_user_id"], user_id["serial_number"]) for user_id in user_ids]
            print(f"User IDs: {user_ids}")

            relevant_phone_numbers = self.db.get_user_from_phone_number_by_serial(serial_number, user_ids[0][0])
            phone_numbers = [phone_number["manager_phone_number"] for phone_number in relevant_phone_numbers]
            
            if not user_ids:
                logger.warning(f"No users found for location {location_id}")
                return
            
            # Parse user IDs if it's a string
            if isinstance(user_ids, str):
                try:
                    user_ids = json.loads(user_ids)
                except json.JSONDecodeError:
                    user_ids = [user_ids]

            # Send SMS to all phone numbers
            if 'water_leak' in payload:
                message = f"""
                Senchi HomeGuard has detected a water leak at {location_id}. \n\nPlease respond with 'Yes' to turn off the shutoff valve, or 'No' to leave it on.
                """
                for phone_number in phone_numbers:
                    print(f"Sending SMS to {phone_number}")
                    try:
                        self.sms_service.send_sms(message, phone_number)
                        logger.info(f"Successfully sent SMS to {phone_number}")
                    except Exception as e:
                        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            
            # Get push tokens for all users
            push_tokens = []
            for user_id in user_ids:
                serial_number = user_id[1]
                tokens = self.db.get_device_tokens_for_iot_device(serial_number)
                if tokens:
                    # Extract device_token from RealDictRow objects
                    for token_row in tokens:
                        if token_row.get('device_token'):
                            push_tokens.append(token_row['device_token'])
            
            if push_tokens:
                notification = await self._create_notification(topic, payload)

                if notification:
                    await self._send_push_notifications(push_tokens, notification)
                
                logger.info(f"Routed message to {len(push_tokens)} users for location {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to route MQTT message: {e}")
    
    async def _create_notification(self, topic: str, payload: dict) -> Optional[NotificationPayload]:
        """Create notification based on MQTT message"""
        # Example: Handle leak detection
        # TODO: Generalize this to handle other types of notifications
        if 'water_leak' in payload and payload['water_leak']:
            device_name = topic.split('/')[-1] if '/' in topic else "Unknown Device"
            return NotificationPayload(
                title="Water Leak Detected!",
                body=f"Leak detected: {device_name}",
                data={
                    "type": "leak_alert",
                    "topic": topic,
                    "payload": payload,
                    "timestamp": datetime.now().isoformat()
                },
                priority="high"
            )
        return
    
    async def _send_push_notifications(self, push_tokens: List[str], notification: NotificationPayload):
        """Send push notifications to devices"""
        try:
            
            # Prepare notification data
            data = {
                "type": notification.data.get("type", "device_update"),
                "topic": notification.data.get("topic", ""),
                "payload": notification.data.get("payload", {}),
                "timestamp": notification.data.get("timestamp", datetime.now().isoformat())
            }
            
            # Determine category and priority based on notification type
            category = "LEAK_ALERT" if notification.data.get("type") == "leak_alert" else "DEVICE_UPDATE"
            
            # Send notifications via APNs
            results = await self.apns_service.send_bulk_notifications(
                device_tokens=push_tokens,
                title=notification.title,
                body=notification.body,
                data=data,
                category=category
            )
            
            # Log results
            success_count = sum(1 for success in results.values() if success)
            logger.info(f"APNs notification sent to {success_count}/{len(push_tokens)} devices")
            
            # Log any failures
            for device_token, success in results.items():
                if not success:
                    logger.warning(f"Failed to send notification to device {str(device_token)[:8]}...")
                    
        except ImportError:
            logger.warning("APNs service not available, falling back to logging")
            logger.info(f"Sending notification to {len(push_tokens)} devices:")
            logger.info(f"Title: {notification.title}")
            logger.info(f"Body: {notification.body}")
            logger.info(f"Data: {notification.data}")
        except Exception as e:
            logger.error(f"Failed to send push notifications: {e}")
            # Fallback to logging
            logger.info(f"Notification (failed to send): {notification.title} - {notification.body}")
    
    # TODO: Periodically check / invalidate tokens that are expired
    async def update_push_token(self, jwt_token: str, new_push_token: str):
        """Update user's push notification token"""
        try:
            user_info = await self.validate_token(jwt_token)
            if not user_info:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = user_info["user_id"]
            
            self.db.register_device_token(
                user_id=user_id,
                device_token=new_push_token,
                platform="apns",
                device_identifier=new_push_token, # TODO: Fix
                device_info={}
            )
            
        except Exception as e:
            logger.error(f"Failed to update push token: {e}")
            raise HTTPException(status_code=500, detail="Push token update failed")