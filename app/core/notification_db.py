"""
Notification Database Operations for DietNotify
Handles FCM tokens and notification preferences in Supabase
"""
import requests
from datetime import datetime
from .database import SUPABASE_URL, get_headers


# ============== NOTIFICATION TOKENS ==============

def save_notification_token(user_id: str, fcm_token: str, device_info: dict = None) -> dict:
    """
    Save or update FCM device token for a user.
    Each device gets its own token entry.
    """
    token_data = {
        "user_id": user_id,
        "fcm_token": fcm_token,
        "device_info": device_info or {},
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Check if token already exists
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notification_tokens",
            headers=get_headers(),
            params={"fcm_token": f"eq.{fcm_token}", "limit": "1"}
        )
        
        if response.status_code == 200:
            existing = response.json()
            
            if existing:
                # Update existing token
                response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/notification_tokens",
                    headers=get_headers(),
                    params={"fcm_token": f"eq.{fcm_token}"},
                    json=token_data
                )
            else:
                # Insert new token
                token_data["created_at"] = datetime.utcnow().isoformat()
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/notification_tokens",
                    headers=get_headers(),
                    json=token_data
                )
            
            if 200 <= response.status_code < 300:
                # Handle empty response (representaton=minimal or 204)
                if not response.text or response.status_code == 204:
                    return token_data
                result = response.json()
                print(f"[NotificationDB] Token saved for user: {user_id}")
                return result[0] if result else token_data
            else:
                print(f"[NotificationDB] Save token error! Status: {response.status_code}")
                print(f"[NotificationDB] Response: {response.text}")
                return None
                
        return None
    except Exception as e:
        print(f"[NotificationDB] Save token exception: {e}")
        return None


def get_user_tokens(user_id: str) -> list:
    """Get all FCM tokens for a user (multiple devices)."""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notification_tokens",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}"}
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"[NotificationDB] Get tokens error: {e}")
        return []


def delete_notification_token(user_id: str, fcm_token: str) -> bool:
    """Delete a specific FCM token."""
    try:
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/notification_tokens",
            headers=get_headers(),
            params={
                "user_id": f"eq.{user_id}",
                "fcm_token": f"eq.{fcm_token}"
            }
        )
        
        if response.status_code in [200, 204]:
            print(f"[NotificationDB] Token deleted for user: {user_id}")
            return True
        return False
    except Exception as e:
        print(f"[NotificationDB] Delete token error: {e}")
        return False


def delete_all_user_tokens(user_id: str) -> bool:
    """Delete all tokens for a user."""
    try:
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/notification_tokens",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}"}
        )
        
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"[NotificationDB] Delete all tokens error: {e}")
        return False


# ============== NOTIFICATION PREFERENCES ==============

def save_notification_preferences(user_id: str, preferences: dict) -> dict:
    """Save user's notification preferences (upsert)."""
    pref_data = {
        "user_id": user_id,
        "enabled": preferences.get('enabled', True),
        "lead_time_minutes": preferences.get('lead_time_minutes', 5),
        "custom_timings": preferences.get('custom_timings', {}),
        "quiet_hours_start": preferences.get('quiet_hours_start'),
        "quiet_hours_end": preferences.get('quiet_hours_end'),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Check if preferences exist
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notification_preferences",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}", "limit": "1"}
        )
        
        if response.status_code == 200:
            existing = response.json()
            
            if existing:
                # Update
                response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/notification_preferences",
                    headers=get_headers(),
                    params={"user_id": f"eq.{user_id}"},
                    json=pref_data
                )
            else:
                # Insert
                pref_data["created_at"] = datetime.utcnow().isoformat()
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/notification_preferences",
                    headers=get_headers(),
                    json=pref_data
                )
            
            if 200 <= response.status_code < 300:
                # Handle empty response
                if not response.text or response.status_code == 204:
                    return pref_data
                result = response.json()
                print(f"[NotificationDB] Preferences saved for user: {user_id}")
                return result[0] if result else pref_data
            else:
                print(f"[NotificationDB] Save preferences error! Status: {response.status_code}")
                print(f"[NotificationDB] Response: {response.text}")
                return None
                
        return None
    except Exception as e:
        print(f"[NotificationDB] Save preferences exception: {e}")
        return None


def get_notification_preferences(user_id: str) -> dict:
    """Get user's notification preferences."""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notification_preferences",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}", "limit": "1"}
        )
        
        if response.status_code == 200:
            prefs = response.json()
            return prefs[0] if prefs else None
        return None
    except Exception as e:
        print(f"[NotificationDB] Get preferences error: {e}")
        return None


def get_all_enabled_preferences() -> list:
    """Get all enabled notification preferences for job restoration."""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notification_preferences",
            headers=get_headers(),
            params={"enabled": "eq.true"}
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"[NotificationDB] Get all enabled prefs error: {e}")
        return []
