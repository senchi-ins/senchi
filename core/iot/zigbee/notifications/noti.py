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
    
    async def create_user_token(self, device_serial: str, push_token: Optional[str] = None) -> TokenResponse:
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
            
            await self._store_token_mappings(user_id, location_id, jwt_token, push_token, expires)
            
            return TokenResponse(
                jwt_token=jwt_token,
                expires_at=expires.isoformat(),
                location_id=location_id
            )
            
        except Exception as e:
            logger.error(f"Failed to create user token: {e}")
            raise HTTPException(status_code=500, detail="Token creation failed")
    
    async def _store_token_mappings(self, user_id: str, location_id: str, jwt_token: str, 
                                   push_token: Optional[str], expires: datetime):
        ttl_seconds = int((expires - datetime.now()).total_seconds())
        
        token_data = {
            "user_id": user_id,
            "location_id": location_id,
            "created_at": datetime.utcnow().isoformat()
        }
        await self.redis_db.set_key(f"jwt:{jwt_token}", json.dumps(token_data), ttl_seconds)
        
        await self.redis_db.set_key(f"user:{user_id}:location", location_id, ttl_seconds)
        
        await self.redis_db.set_key(f"location:{location_id}:users", user_id, ttl_seconds)
        
        if push_token:
            await self.redis_db.set_key(f"user:{user_id}:push_token", push_token, ttl_seconds)
            await self.redis_db.set_key(f"push_token:{push_token}", user_id, ttl_seconds)
    
    async def route_mqtt_message(self, topic: str, payload: dict):
        """Route MQTT message to correct users"""
        try:
            # Extract location from topic: zigbee2mqtt/rpi-zigbee-abc123/device/event
            topic_parts = topic.split('/')
            if len(topic_parts) < 2:
                return
            
            location_id = topic_parts[1]  # e.g., "rpi-zigbee-abc123"
            
            # Get all users for this location
            user_ids = await self.redis.smembers(f"location:{location_id}:users")
            
            if not user_ids:
                logger.warning(f"No users found for location {location_id}")
                return
            
            # Get push tokens for all users
            push_tokens = []
            for user_id in user_ids:
                token = await self.redis.get(f"user:{user_id}:push_token")
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
        # TODO: Integrate with Apple Push Notification Service
        # For now, just log the notification
        logger.info(f"Sending notification to {len(push_tokens)} devices:")
        logger.info(f"Title: {notification.title}")
        logger.info(f"Body: {notification.body}")
        logger.info(f"Data: {notification.data}")
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user info"""
        try:
            token_data = await self.redis_db.get_key(f"jwt:{token}")
            if not token_data:
                return None
            
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
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
            
            # Get token TTL and apply to push token
            ttl = await self.redis.ttl(f"jwt:{jwt_token}")
            if ttl > 0:
                await self.redis.setex(f"user:{user_id}:push_token", ttl, new_push_token)
                await self.redis.setex(f"push_token:{new_push_token}", ttl, user_id)
            
        except Exception as e:
            logger.error(f"Failed to update push token: {e}")
            raise HTTPException(status_code=500, detail="Push token update failed")