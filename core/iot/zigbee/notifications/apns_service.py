import os
import json
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

logger = logging.getLogger(__name__)

class APNsService:
    """Apple Push Notification Service integration"""
    
    def __init__(self):
        self.auth_key_path = os.getenv("APNS_AUTH_KEY_PATH")
        self.key_id = os.getenv("APNS_KEY_ID")
        self.team_id = os.getenv("APNS_TEAM_ID")
        self.bundle_id = os.getenv("APNS_BUNDLE_ID", "com.senchi.homemonitor")
        
        # APNs endpoints
        self.sandbox_url = "https://api.sandbox.push.apple.com"
        self.production_url = "https://api.push.apple.com"
        
        # Use sandbox for development, production for release
        self.is_production = os.getenv("APNS_PRODUCTION", "false").lower() == "true"
        self.base_url = self.production_url if self.is_production else self.sandbox_url
        
        self._auth_token = None
        self._token_expiry = None
        
        logger.info(f"APNs initialized - Production: {self.is_production}, Bundle ID: {self.bundle_id}")
    
    def _load_auth_key(self) -> Optional[bytes]:
        """Load the APNs authentication key"""
        if not self.auth_key_path or not os.path.exists(self.auth_key_path):
            logger.error(f"APNs auth key not found at: {self.auth_key_path}")
            return None
        
        try:
            with open(self.auth_key_path, 'rb') as key_file:
                return key_file.read()
        except Exception as e:
            logger.error(f"Failed to load APNs auth key: {e}")
            return None
    
    def _generate_auth_token(self) -> Optional[str]:
        """Generate JWT token for APNs authentication"""
        auth_key_data = self._load_auth_key()
        if not auth_key_data:
            return None
        
        try:
            # Load the private key
            private_key = serialization.load_pem_private_key(
                auth_key_data,
                password=None
            )
            
            # Create JWT token
            now = datetime.utcnow()
            payload = {
                'iss': self.team_id,
                'iat': int(now.timestamp())
            }
            
            headers = {
                'kid': self.key_id,
                'alg': 'ES256'
            }
            
            token = jwt.encode(
                payload,
                private_key,
                algorithm='ES256',
                headers=headers
            )
            
            self._auth_token = token
            self._token_expiry = now.timestamp() + 3600  # 1 hour expiry
            
            logger.info("APNs auth token generated successfully")
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate APNs auth token: {e}")
            return None
    
    def _get_auth_token(self) -> Optional[str]:
        """Get valid auth token, generating new one if needed"""
        now = datetime.utcnow().timestamp()
        
        if (not self._auth_token or 
            not self._token_expiry or 
            now >= self._token_expiry):
            return self._generate_auth_token()
        
        return self._auth_token
    
    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
        badge: int = None,
        sound: str = "default",
        category: str = "LEAK_ALERT"
    ) -> bool:
        """Send push notification to a single device"""
        
        auth_token = self._get_auth_token()
        if not auth_token:
            logger.error("No valid APNs auth token available")
            return False
        
        # Prepare notification payload
        aps_payload = {
            "alert": {
                "title": title,
                "body": body
            },
            "sound": sound,
            "category": category
        }
        
        if badge is not None:
            aps_payload["badge"] = badge
        
        payload = {
            "aps": aps_payload
        }
        
        # Add custom data if provided
        if data:
            payload.update(data)
        
        # Prepare headers
        headers = {
            "Authorization": f"bearer {auth_token}",
            "apns-topic": self.bundle_id,
            "apns-push-type": "alert",
            "Content-Type": "application/json"
        }
        
        # Add priority for high-priority notifications (like leaks)
        if category == "LEAK_ALERT":
            headers["apns-priority"] = "10"
        
        url = f"{self.base_url}/3/device/{device_token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"APNs notification sent successfully to {device_token[:8]}...")
                        return True
                    else:
                        response_text = await response.text()
                        logger.error(f"APNs notification failed: {response.status} - {response_text}")
                        
                        # Handle specific APNs errors
                        if response.status == 410:
                            logger.warning(f"Device token {device_token[:8]}... is no longer valid")
                        elif response.status == 400:
                            logger.error(f"Invalid payload for device {device_token[:8]}...")
                        
                        return False
                        
        except Exception as e:
            logger.error(f"APNs request failed: {e}")
            return False
    
    async def send_bulk_notifications(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Dict[str, Any] = None,
        badge: int = None,
        sound: str = "default",
        category: str = "LEAK_ALERT"
    ) -> Dict[str, bool]:
        """Send notifications to multiple devices"""
        
        results = {}
        tasks = []
        
        for device_token in device_tokens:
            task = self.send_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data,
                badge=badge,
                sound=sound,
                category=category
            )
            tasks.append((device_token, task))
        
        # Execute all notifications concurrently
        for device_token, task in tasks:
            try:
                success = await task
                results[device_token] = success
            except Exception as e:
                logger.error(f"Failed to send notification to {device_token[:8]}...: {e}")
                results[device_token] = False
        
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"Bulk notification complete: {success_count}/{len(device_tokens)} successful")
        
        return results

# Global APNs service instance
apns_service = APNsService() 