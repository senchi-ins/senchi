import os


# Notifications
NOTIFICATION_CONFIG = {
    "JWT_SECRET": os.getenv("JWT_SECRET", "your-secret-key"),
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRY_HOURS": 24 * 30  # 30 days
}