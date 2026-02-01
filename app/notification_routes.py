"""
Notification Routes for DietNotify
API endpoints for managing push notifications and preferences
"""
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app, render_template
import os
from .services.notification_service import get_scheduler, init_notifications
from .core.database import (
    get_active_plan, get_profile
)
from .core.notification_db import (
    save_notification_token, get_user_tokens, delete_notification_token,
    save_notification_preferences, get_notification_preferences
)
from .core.firebase_config import get_firebase_web_config

notification_bp = Blueprint('notifications', __name__)


# Serve Firebase service worker from root (required by Firebase)
@notification_bp.route('/firebase-messaging-sw.js')
def firebase_sw():
    """Serve Firebase service worker from root path."""
    static_dir = os.path.join(current_app.root_path, 'static')
    return send_from_directory(static_dir, 'firebase-messaging-sw.js', 
                               mimetype='application/javascript')


def is_authenticated():
    return 'user_id' in session


def get_current_user():
    return session.get('user_id')


# ============== DEVICE TOKEN MANAGEMENT ==============

@notification_bp.route('/api/notifications/register', methods=['POST'])
def register_token():
    """Register a device FCM token for push notifications."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    device_info = data.get('device_info', {})
    
    if not token:
        return jsonify({"error": "Token required"}), 400
    
    user_id = get_current_user()
    result = save_notification_token(user_id, token, device_info)
    
    if result:
        # Also schedule notifications if user has an active diet plan
        active_plan = get_active_plan(user_id)
        if active_plan:
            preferences = get_notification_preferences(user_id)
            if preferences and preferences.get('enabled', True):
                scheduler = get_scheduler()
                plan_data = active_plan.get('plan_data', {})
                lead_time = preferences.get('lead_time_minutes', 5)
                custom_timings = preferences.get('custom_timings', {})
                
                job_ids = scheduler.schedule_from_diet_plan(
                    user_id=user_id,
                    diet_plan=plan_data,
                    tokens=[token],
                    lead_time_minutes=lead_time,
                    custom_timings=custom_timings
                )
                
                return jsonify({
                    "success": True,
                    "message": "Token registered and notifications scheduled",
                    "scheduled_meals": len(job_ids)
                })
        
        return jsonify({
            "success": True,
            "message": "Token registered successfully"
        })
    
    return jsonify({"error": "Failed to register token"}), 500


@notification_bp.route('/api/notifications/unregister', methods=['POST'])
def unregister_token():
    """Remove a device token (disable notifications for this device)."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token required"}), 400
    
    user_id = get_current_user()
    result = delete_notification_token(user_id, token)
    
    if result:
        return jsonify({"success": True, "message": "Token unregistered"})
    
    return jsonify({"error": "Failed to unregister token"}), 500


# ============== NOTIFICATION PREFERENCES ==============

@notification_bp.route('/api/notifications/preferences', methods=['GET'])
def get_preferences():
    """Get user's notification preferences."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = get_current_user()
    prefs = get_notification_preferences(user_id)
    
    # Return defaults if no preferences saved
    if not prefs:
        prefs = {
            "enabled": False,
            "lead_time_minutes": 5,
            "custom_timings": {},
            "quiet_hours_start": None,
            "quiet_hours_end": None
        }
    
    return jsonify(prefs)


@notification_bp.route('/api/notifications/preferences', methods=['POST'])
def update_preferences():
    """Update user's notification preferences."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    user_id = get_current_user()
    
    # Get existing preferences to merge
    existing = get_notification_preferences(user_id) or {}
    
    # Construct complete prefs object by merging
    prefs = {
        "enabled": data.get('enabled', existing.get('enabled', True)),
        "lead_time_minutes": data.get('lead_time_minutes', existing.get('lead_time_minutes', 5)),
        "custom_timings": data.get('custom_timings', existing.get('custom_timings', {})),
        "quiet_hours_start": data.get('quiet_hours_start', existing.get('quiet_hours_start')),
        "quiet_hours_end": data.get('quiet_hours_end', existing.get('quiet_hours_end'))
    }
    
    result = save_notification_preferences(user_id, prefs)
    
    if not result:
        return jsonify({"success": False, "error": "Database error while saving preferences"}), 500
    
    if result:
        # Reschedule notifications if enabled
        if prefs['enabled']:
            active_plan = get_active_plan(user_id)
            tokens = get_user_tokens(user_id)
            
            if active_plan and tokens:
                scheduler = get_scheduler()
                scheduler.cancel_user_notifications(user_id)
                
                token_list = [t['fcm_token'] for t in tokens]
                job_ids = scheduler.schedule_from_diet_plan(
                    user_id=user_id,
                    diet_plan=active_plan.get('plan_data', {}),
                    tokens=token_list,
                    lead_time_minutes=prefs['lead_time_minutes'],
                    custom_timings=prefs.get('custom_timings', {})
                )
                
                return jsonify({
                    "success": True,
                    "message": "Preferences updated",
                    "scheduled_meals": len(job_ids)
                })
        else:
            # Disable - cancel all notifications
            scheduler = get_scheduler()
            cancelled = scheduler.cancel_user_notifications(user_id)
            return jsonify({
                "success": True,
                "message": "Notifications disabled",
                "cancelled": cancelled
            })
        
        return jsonify({"success": True, "message": "Preferences updated"})
    
    return jsonify({"error": "Failed to update preferences"}), 500


# ============== NOTIFICATION SCHEDULING ==============

@notification_bp.route('/api/notifications/schedule', methods=['POST'])
def schedule_notifications():
    """Schedule notifications from active diet plan."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = get_current_user()
    
    # Get user's active diet plan
    active_plan = get_active_plan(user_id)
    if not active_plan:
        return jsonify({"error": "No active diet plan found"}), 404
    
    # Get user's device tokens
    tokens = get_user_tokens(user_id)
    if not tokens:
        return jsonify({"error": "No registered devices found"}), 400
    
    # Get preferences
    prefs = get_notification_preferences(user_id)
    lead_time = prefs.get('lead_time_minutes', 5) if prefs else 5
    
    # Schedule notifications
    scheduler = get_scheduler()
    scheduler.cancel_user_notifications(user_id)  # Clear old schedules
    
    token_list = [t['fcm_token'] for t in tokens]
    plan_data = active_plan.get('plan_data', {})
    custom_timings = prefs.get('custom_timings', {}) if prefs else {}
    
    job_ids = scheduler.schedule_from_diet_plan(
        user_id=user_id,
        diet_plan=plan_data,
        tokens=token_list,
        lead_time_minutes=lead_time,
        custom_timings=custom_timings
    )
    
    return jsonify({
        "success": True,
        "scheduled": len(job_ids),
        "jobs": job_ids
    })


@notification_bp.route('/api/notifications/status', methods=['GET'])
def get_status():
    """Get current notification status for user."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = get_current_user()
    
    # Get tokens
    tokens = get_user_tokens(user_id)
    
    # Get preferences
    prefs = get_notification_preferences(user_id)
    
    # Get scheduled jobs
    scheduler = get_scheduler()
    jobs = scheduler.get_user_jobs(user_id)
    
    return jsonify({
        "registered_devices": len(tokens) if tokens else 0,
        "enabled": prefs.get('enabled', False) if prefs else False,
        "lead_time_minutes": prefs.get('lead_time_minutes', 5) if prefs else 5,
        "scheduled_reminders": len(jobs),
        "reminders": jobs
    })


# ============== TEST & DEBUG ==============

@notification_bp.route('/notifications/debug')
def debug_page():
    """Render notification debug page."""
    return render_template('notification_debug.html')

@notification_bp.route('/api/notifications/test', methods=['POST'])
def send_test():
    """Send a test notification to verify setup."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    
    if not token:
        # Try to get user's first registered token
        user_id = get_current_user()
        tokens = get_user_tokens(user_id)
        if tokens:
            token = tokens[0]['fcm_token']
        else:
            return jsonify({"error": "No token provided or registered"}), 400
    
    try:
        scheduler = get_scheduler()
        success = scheduler.send_test_notification(token)
        
        if success:
            return jsonify({"success": True, "message": "Test notification sent!"})
        
        return jsonify({"error": "Failed to send test notification"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@notification_bp.route('/api/notifications/debug/force_fire', methods=['POST'])
def force_fire_notification():
    """Debug: Force send a specific meal notification immediately."""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    meal_name = data.get('meal_name')
    
    if not meal_name:
        return jsonify({"error": "Meal name required"}), 400
        
    user_id = get_current_user()
    tokens = get_user_tokens(user_id)
    
    if not tokens:
        return jsonify({"error": "No devices registered"}), 400
        
    try:
        token_list = [t['fcm_token'] for t in tokens]
        
        # Construct ad-hoc notification
        title = f"🍽️ {meal_name} (Test)"
        body = f"This is a test run for your '{meal_name}' reminder."
        
        from .core.firebase_config import send_push_notification
        
        success_count = 0
        for token in token_list:
             res = send_push_notification(
                token=token,
                title=title,
                body=body,
                data={
                    "type": "meal_reminder",
                    "meal_name": meal_name,
                    "user_id": user_id,
                    "is_test": "true"
                }
            )
             if res: success_count += 1
             
        return jsonify({
            "success": True, 
            "message": f"Sent to {success_count}/{len(token_list)} devices",
            "device_count": len(token_list)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notification_bp.route('/api/notifications/firebase-config', methods=['GET'])
def get_firebase_config():
    """Get Firebase config for frontend initialization."""
    config = get_firebase_web_config()
    return jsonify(config)
