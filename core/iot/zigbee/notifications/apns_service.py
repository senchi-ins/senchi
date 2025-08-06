import os
import json
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from dotenv import load_dotenv
import httpx

load_dotenv()

logger = logging.getLogger(__name__)


class APNsService:
    """Apple Push Notification Service integration"""
    
    def __init__(self):
        self.auth_key = os.getenv("APNS_AUTH_KEY")
        self.key_id = os.getenv("APNS_KEY_ID")
        self.team_id = os.getenv("APNS_TEAM_ID")
        self.bundle_id = os.getenv("APNS_BUNDLE_ID", "com.mdawes.senchi")
        
        self.sandbox_url = "https://api.development.push.apple.com"
        self.production_url = "https://api.push.apple.com"
        
        self.is_production = os.getenv("APNS_PRODUCTION", "false").lower() == "true"
        self.base_url = self.production_url if self.is_production else self.sandbox_url
        
        self._auth_token = None
        self._token_expiry = None
        self.token_duration_hours = 24 * 30 * 6 # 6 months
        
        logger.info(f"APNs initialized - Production: {self.is_production}, Bundle ID: {self.bundle_id}")
    
    
    def _generate_auth_token(self) -> Optional[str]:
        """Generate JWT token for APNs authentication"""
        if not self.auth_key:
            logger.error("APNs auth key not provided")
            return None
        
        try:
            # Load the private key from the PEM string
            private_key = serialization.load_pem_private_key(
                self.auth_key.encode('utf-8'),
                password=None
            )
            
            # Create JWT token
            now = datetime.now()
            expiry_time = now + timedelta(hours=self.token_duration_hours)
            payload = {
                'iss': self.team_id,
                'iat': int(now.timestamp()),
                'exp': int(expiry_time.timestamp())
            }

            print(payload)
            
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
            self._token_expiry = expiry_time.timestamp()
            
            logger.info("APNs auth token generated successfully")
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate APNs auth token: {e}")
            return None
    
    def _get_auth_token(self) -> Optional[str]:
        # TODO: Add caching of the token
        return self._generate_auth_token()
    
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
            "authorization": f"bearer {auth_token}",
            "apns-topic": self.bundle_id,
            "apns-push-type": "alert",
            "apns-priority": "10",
            "apns-expiration": "0",
            "content-type": "application/json"
        }
        
        # Add priority for high-priority notifications (like leaks)
        if category == "LEAK_ALERT":
            headers["apns-priority"] = "10"
        
        url = f"{self.base_url}/3/device/{device_token}"

        try:
            async with httpx.AsyncClient(http2=True, timeout=10) as client:
                response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                logger.info(f"APNs notification sent successfully to {str(device_token)[:8]}...")
                return True
            else:
                logger.error(f"APNs notification failed: {response.status_code} - {response.text}")
                logger.error(f"APNs response headers: {dict(response.headers)}")
                logger.error(f"APNs request URL: {url}")
                logger.error(f"APNs request headers: {headers}")
                logger.error(f"APNs request payload: {json.dumps(payload)}")
                # Handle specific APNs errors
                if response.status_code == 410:
                    logger.warning(f"Device token {str(device_token)[:8]}... is no longer valid")
                elif response.status_code == 400:
                    logger.error(f"Invalid payload for device {str(device_token)[:8]}...")
                return False
                        
        except Exception as e:
            logger.error(f"APNs request failed for device {str(device_token)[:8]}...: {e}")
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
                logger.error(f"Failed to send notification to {str(device_token)[:8]}...: {e}")
                results[device_token] = False
        
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"Bulk notification complete: {success_count}/{len(device_tokens)} successful")
        
        return results

# Global APNs service instance
apns_service = APNsService() 

if __name__ == "__main__":
    apns = APNsService()