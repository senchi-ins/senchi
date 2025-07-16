import jwt
import uuid
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import HTTPException
from models.tokens import TokenResponse, NotificationPayload
from rdsdb.rdsdb import RedisDB
from cfg import NOTIFICATION_CONFIG

logger = logging.getLogger(__name__)


class NotificationRouter:
    def __init__(self, redis_db: RedisDB):
        self.redis_db = redis_db
    
    async def create_user_token(self, device_serial: str, push_token: Optional[str] = None, email: Optional[str] = None) -> TokenResponse:
        """Create JWT token for a user during device setup"""
        try:
            location_id = f"rpi-zigbee-{device_serial[-8:]}"
            user_id = str(uuid.uuid4())
            
            now = datetime.now()
            expires = now + timedelta(hours=NOTIFICATION_CONFIG["JWT_EXPIRY_HOURS"])
            
            jwt_payload = {
                "user_id": user_id,
                "location_id": location_id,
                "device_serial": device_serial,
                "iat": now.timestamp(),
                "exp": expires.timestamp()
            }
            
            jwt_token = jwt.encode(jwt_payload, NOTIFICATION_CONFIG["JWT_SECRET"], algorithm=NOTIFICATION_CONFIG["JWT_ALGORITHM"])
            
            await self._store_token_mappings(user_id, location_id, jwt_token, push_token, email, expires)

            # --- Store JWT <-> topic mapping in Redis ---
            topic = f"zigbee2mqtt/{location_id}/#"
            # TODO: Store in postgres later
            ttl_seconds = 60 * 60 * 24 * 30  # 30 days
            self.redis_db.set_key(f"jwt:{jwt_token}:topic", topic, ttl_seconds)
            # Store mapping: topic -> JWTs (append to a set or comma-separated string)
            existing_jwts = self.redis_db.get_key(f"topic:{topic}:jwts")
            if existing_jwts:
                jwt_list = set(existing_jwts.decode().split(","))
                jwt_list.add(jwt_token)
                self.redis_db.set_key(f"topic:{topic}:jwts", ",".join(jwt_list), ttl_seconds)
            else:
                self.redis_db.set_key(f"topic:{topic}:jwts", jwt_token, ttl_seconds)
            # --- End JWT <-> topic mapping ---
            
            return TokenResponse(
                jwt_token=jwt_token,
                expires_at=expires.isoformat(),
                location_id=location_id
            )
            
        except Exception as e:
            logger.error(f"Failed to create user token: {e}")
            raise HTTPException(status_code=500, detail="Token creation failed")
    
    async def _store_token_mappings(self, user_id: str, location_id: str, jwt_token: str, 
                                   push_token: Optional[str], email: Optional[str], expires: datetime):
        # ttl_seconds = int((expires - datetime.now()).total_seconds())
        # TODO: Make this dynamic based on the expiry time of the token
        ttl_seconds = 60 * 60 * 24 * 30 # 30 days
        
        token_data = {
            "user_id": user_id,
            "location_id": location_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self.redis_db.set_key(f"jwt:{jwt_token}", json.dumps(token_data), ttl_seconds)
        
        self.redis_db.set_key(f"user:{user_id}:location", location_id, ttl_seconds)
        
        self.redis_db.set_key(f"location:{location_id}:users", user_id, ttl_seconds)
        
        if push_token:
            self.redis_db.set_key(f"user:{user_id}:push_token", push_token, ttl_seconds)
            self.redis_db.set_key(f"push_token:{push_token}", user_id, ttl_seconds)
        
        # Store email -> token mapping for login functionality
        if email:
            self.redis_db.set_key(f"email:{email}", jwt_token, ttl_seconds)
            logger.info(f"Stored email -> token mapping for: {email}")
    
    async def route_mqtt_message(self, topic: str, payload: dict):
        """Route MQTT message to correct users"""
        try:
            # Extract location from topic: zigbee2mqtt/rpi-zigbee-abc123/device/event
            topic_parts = topic.split('/')
            if len(topic_parts) < 2:
                return
            
            location_id = topic_parts[1]  # e.g., "rpi-zigbee-abc123"
            
            # Get all users for this location
            user_ids = self.redis_db.get_key(f"location:{location_id}:users")
            
            if not user_ids:
                logger.warning(f"No users found for location {location_id}")
                return
            
            # Parse user IDs if it's a string
            if isinstance(user_ids, str):
                try:
                    user_ids = json.loads(user_ids)
                except json.JSONDecodeError:
                    user_ids = [user_ids]
            
            # Get push tokens for all users
            push_tokens = []
            for user_id in user_ids:
                token = self.redis_db.get_key(f"user:{user_id}:push_token")
                if token:
                    push_tokens.append(token)
            
            if push_tokens:
                notification = await self._create_notification(topic, payload)
                
                await self._send_push_notifications(push_tokens, notification)
                
                logger.info(f"Routed message to {len(push_tokens)} users for location {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to route MQTT message: {e}")
    
    async def _create_notification(self, topic: str, payload: dict) -> NotificationPayload:
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
        
        return NotificationPayload(
            title="Device Update",
            body="Your device has been updated",
            data={"type": "device_update", "topic": topic, "payload": payload}
        )
    
    async def _send_push_notifications(self, push_tokens: List[str], notification: NotificationPayload):
        """Send push notifications to devices"""
        try:
            from .apns_service import apns_service
            
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
            results = await apns_service.send_bulk_notifications(
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
                    logger.warning(f"Failed to send notification to device {device_token[:8]}...")
                    
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
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user info"""
        try:
            token_data = self.redis_db.get_key(f"jwt:{token}")
            if not token_data:
                return None
            
            payload = jwt.decode(token, NOTIFICATION_CONFIG["JWT_SECRET"], algorithms=[NOTIFICATION_CONFIG["JWT_ALGORITHM"]])
            
            redis_data = json.loads(token_data)
            return {**payload, **redis_data}
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    async def update_push_token(self, jwt_token: str, new_push_token: str):
        """Update user's push notification token"""
        try:
            user_info = await self.validate_token(jwt_token)
            if not user_info:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = user_info["user_id"]
            
            # Set TTL to 30 days for push tokens
            ttl_seconds = 60 * 60 * 24 * 30
            self.redis_db.set_key(f"user:{user_id}:push_token", new_push_token, ttl_seconds)
            self.redis_db.set_key(f"push_token:{new_push_token}", user_id, ttl_seconds)
            
        except Exception as e:
            logger.error(f"Failed to update push token: {e}")
            raise HTTPException(status_code=500, detail="Push token update failed")