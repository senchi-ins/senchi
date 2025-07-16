# Apple Push Notification Service (APNs) Configuration

## Prerequisites

1. **Apple Developer Account** with push notification capability
2. **APNs Authentication Key** (.p8 file) from Apple Developer Console
3. **Team ID** from Apple Developer Account
4. **Key ID** from the authentication key
5. **Bundle ID** of your iOS app

## Setup Steps

### 1. Apple Developer Console Setup

1. Go to [Apple Developer Console](https://developer.apple.com/account/)
2. Navigate to **Certificates, Identifiers & Profiles**
3. Go to **Keys** section
4. Click **+** to create a new key
5. Enable **Apple Push Notifications service (APNs)**
6. Download the `.p8` file (you can only download it once!)
7. Note the **Key ID** (10-character string)

### 2. App Configuration

1. In **Identifiers**, find your app's bundle ID
2. Enable **Push Notifications** capability
3. Note your **Team ID** (10-character string)

### 3. Environment Variables

Add these to your `.env` file or deployment environment:

```bash
# APNs Configuration
APNS_AUTH_KEY_PATH=/path/to/your/AuthKey_KEYID.p8
APNS_KEY_ID=YOUR_KEY_ID
APNS_TEAM_ID=YOUR_TEAM_ID
APNS_BUNDLE_ID=com.senchi.homemonitor
APNS_PRODUCTION=false  # Set to true for production
```

### 4. File Structure

Place your APNs key file in a secure location:

```
iot/zigbee/
├── notifications/
│   ├── apns_service.py
│   ├── apns_config.md
│   └── keys/
│       └── AuthKey_KEYID.p8  # Your APNs key file
```

### 5. Security Considerations

- **Never commit** the `.p8` file to version control
- Use environment variables for sensitive data
- Store keys securely in production (e.g., AWS Secrets Manager, Azure Key Vault)
- Rotate keys periodically

## Testing

### 1. Test Notification Endpoint

Add this to your server for testing:

```python
@app.post("/test-notification")
async def test_notification(device_token: str):
    from notifications.apns_service import apns_service
    
    success = await apns_service.send_notification(
        device_token=device_token,
        title="Test Notification",
        body="This is a test notification from your server",
        data={"type": "test"},
        category="TEST"
    )
    
    return {"success": success}
```

### 2. Test with curl

```bash
curl -X POST "http://your-server:8000/test-notification" \
  -H "Content-Type: application/json" \
  -d '{"device_token": "YOUR_DEVICE_TOKEN"}'
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check your auth key, team ID, and key ID
2. **400 Bad Request**: Invalid payload format
3. **410 Gone**: Device token is no longer valid
4. **403 Forbidden**: Wrong bundle ID or certificate

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('notifications.apns_service').setLevel(logging.DEBUG)
```

## Production Deployment

1. Set `APNS_PRODUCTION=true`
2. Use production APNs endpoint
3. Ensure proper SSL/TLS configuration
4. Monitor notification delivery rates
5. Implement retry logic for failed notifications

## Monitoring

Track notification metrics:
- Delivery success rate
- Device token validity
- Response times
- Error rates by type 