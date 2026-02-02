"""
Firebase Configuration for DietNotify
Push Notification Service using Firebase Cloud Messaging (FCM)

SETUP INSTRUCTIONS:
1. Go to https://console.firebase.google.com/
2. Create new project named "DietNotify"
3. Go to Project Settings > Service Accounts
4. Click "Generate new private key"
5. Save as "firebase-admin-key.json" in this folder (app/core/)
6. IMPORTANT: Add firebase-admin-key.json to .gitignore!
"""
import os
import json
from datetime import datetime

def log_to_file(msg):
    try:
        with open("notification_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    print("[Firebase] firebase-admin not installed. Run: pip install firebase-admin")
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    credentials = None
    messaging = None

# Path to service account key file
# Path to service account key file
# Default to local folder, but allow override via env var (crucial for Render /etc/secrets/)
FIREBASE_KEY_PATH = os.getenv('FIREBASE_KEY_PATH', os.path.join(os.path.dirname(__file__), 'firebase-admin-key.json'))

# Firebase Web Config (for frontend)
FIREBASE_WEB_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

# VAPID Keys for Web Push (from Firebase Console > Cloud Messaging > Web Push certificates)
VAPID_KEY = os.getenv("FIREBASE_VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("FIREBASE_VAPID_PRIVATE_KEY")

# Initialize Firebase Admin SDK
_firebase_app = None

def init_firebase():
    """Initialize Firebase Admin SDK for server-side operations."""
    global _firebase_app
    
    if not FIREBASE_AVAILABLE:
        print("[Firebase] SDK not available - notifications disabled")
        return False
    
    if _firebase_app:
        print("[Firebase] Already initialized")
        return True
    
    if not os.path.exists(FIREBASE_KEY_PATH):
        print(f"[Firebase] Service account key not found at: {FIREBASE_KEY_PATH}")
        print("[Firebase] Please follow setup instructions in this file")
        return False
    
    try:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        print("[Firebase] Admin SDK initialized successfully!")
        return True
    except Exception as e:
        print(f"[Firebase] Initialization error: {e}")
        return False


def send_push_notification(token: str, title: str, body: str, data: dict = None) -> bool:
    """
    Send a push notification to a specific device.
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body text
        data: Optional data payload
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not FIREBASE_AVAILABLE or not _firebase_app:
        print("[Firebase] Not initialized - cannot send notification")
        return False
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon="/static/img/logo.svg",
                    badge="/static/img/logo.svg",
                    vibrate=[200, 100, 200],
                    require_interaction=True,
                    actions=[
                        messaging.WebpushNotificationAction(
                            action="view",
                            title="View Diet Plan"
                        ),
                        messaging.WebpushNotificationAction(
                            action="dismiss",
                            title="Dismiss"
                        )
                    ]
                )
            )
        )
        
        response = messaging.send(message)
        log_to_file(f"[Firebase] Notification sent: {response}")
        print(f"[Firebase] Notification sent: {response}")
        return True
        
    except messaging.UnregisteredError:
        log_to_file(f"[Firebase] Token invalid/unregistered: {token[:20]}...")
        print(f"[Firebase] Token invalid/unregistered: {token[:20]}...")
        return False
    except Exception as e:
        log_to_file(f"[Firebase] Send error: {e}")
        print(f"[Firebase] Send error: {e}")
        return False


def send_bulk_notifications(tokens: list, title: str, body: str, data: dict = None) -> dict:
    """
    Send notifications to multiple devices.
    
    Returns:
        Dict with success_count and failure_count
    """
    if not FIREBASE_AVAILABLE or not _firebase_app:
        return {"success_count": 0, "failure_count": len(tokens), "error": "Firebase not initialized"}
    
    if not tokens:
        return {"success_count": 0, "failure_count": 0}
    
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon="/static/img/logo.svg",
                    badge="/static/img/logo.svg",
                    vibrate=[200, 100, 200],
                )
            )
        )
        
        response = messaging.send_each_for_multicast(message)
        print(f"[Firebase] Bulk send: {response.success_count} success, {response.failure_count} failed")
        
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count
        }
        
    except Exception as e:
        print(f"[Firebase] Bulk send error: {e}")
        return {"success_count": 0, "failure_count": len(tokens), "error": str(e)}


def get_firebase_web_config() -> dict:
    """Get Firebase config for frontend JavaScript."""
    return {
        "config": FIREBASE_WEB_CONFIG,
        "vapidKey": VAPID_KEY
    }


# Auto-initialize on import (optional, can be called manually)
# init_firebase()
