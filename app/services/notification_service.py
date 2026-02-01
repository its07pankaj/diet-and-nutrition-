"""
Notification Service for DietNotify
Handles scheduling and sending meal reminder notifications
Uses APScheduler for background job scheduling
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pytz

# APScheduler for background jobs
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    print("[Notifications] APScheduler not installed. Run: pip install apscheduler")
    SCHEDULER_AVAILABLE = False
    BackgroundScheduler = None

from app.core.firebase_config import send_push_notification, send_bulk_notifications, init_firebase
from app.core.notification_db import get_all_enabled_preferences, get_user_tokens
from app.core.database import get_active_plan


class NotificationScheduler:
    """
    Manages meal reminder notifications based on diet plans.
    """
    
    def __init__(self, timezone: str = "Asia/Kolkata"):
        self.timezone = pytz.timezone(timezone)
        self.scheduler = None
        self._initialized = False
        
        if SCHEDULER_AVAILABLE:
            self.scheduler = BackgroundScheduler(timezone=self.timezone)
        else:
            print("[Notifications] Scheduler unavailable - notifications disabled")
    
    def start(self):
        """Start the background scheduler."""
        if self.scheduler and not self._initialized:
            self.scheduler.start()
            self._initialized = True
            self._log("Scheduler started!")
            return True
        return False
    
    def _log(self, message: str):
        """Log message to console and file."""
        msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [Notifications] {message}"
        print(msg)
        try:
            with open("notification_debug.log", "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except:
            pass

    def restore_jobs(self):
        """Restore scheduled jobs from database on startup."""
        try:
            print("[Notifications] Restoring scheduled jobs...")
            
            # Clear existing jobs to ensure clean slate (User request)
            if self.scheduler:
                self.scheduler.remove_all_jobs()
                print("[Notifications] Cleared previous jobs")
            
            preferences_list = get_all_enabled_preferences()
            
            restored_count = 0
            for pref in preferences_list:
                user_id = pref.get('user_id')
                if not user_id:
                    continue
                
                # Get active plan
                active_plan = get_active_plan(user_id)
                if not active_plan:
                    continue
                
                # Get tokens
                tokens = get_user_tokens(user_id)
                if not tokens:
                    continue
                
                token_list = [t['fcm_token'] for t in tokens]
                active_plan_data = active_plan.get('plan_data', {})
                lead_time = pref.get('lead_time_minutes', 5)
                custom_timings = pref.get('custom_timings', {})
                
                job_ids = self.schedule_from_diet_plan(
                    user_id=user_id,
                    diet_plan=active_plan_data,
                    tokens=token_list,
                    lead_time_minutes=lead_time,
                    custom_timings=custom_timings
                )
                restored_count += len(job_ids)
            
            self._log(f"Restored {restored_count} notifications for {len(preferences_list)} users")
            return restored_count
            
        except Exception as e:
            print(f"[Notifications] Restoration error: {e}")
            self._log(f"Restoration failed: {e}")
            return 0
    
    def stop(self):
        """Stop the scheduler gracefully."""
        if self.scheduler and self._initialized:
            self.scheduler.shutdown(wait=False)
            self._initialized = False
            print("[Notifications] Scheduler stopped")
    
    def schedule_meal_reminder(
        self,
        user_id: str,
        meal_name: str,
        meal_time: str,
        tokens: List[str],
        lead_time_minutes: int = 5,
        meal_items: List[str] = None
    ) -> Optional[str]:
        """
        Schedule a notification for a specific meal.
        
        Args:
            user_id: User identifier
            meal_name: Name of the meal (e.g., "Metabolic Ignition Breakfast")
            meal_time: Time string (e.g., "7:00 AM" or "07:00")
            tokens: List of FCM device tokens
            lead_time_minutes: Minutes before meal time to send notification
            meal_items: List of food items in the meal
        
        Returns:
            Job ID if scheduled successfully, None otherwise
        """
        if not self.scheduler:
            return None
        
        # Parse meal time
        try:
            # Handle various time formats
            time_formats = ["%I:%M %p", "%H:%M", "%I:%M%p"]
            parsed_time = None
            
            for fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(meal_time.strip(), fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                print(f"[Notifications] Could not parse time: {meal_time}")
                return None
            
            # Calculate notification time (meal time - lead time)
            notify_hour = parsed_time.hour
            notify_minute = parsed_time.minute - lead_time_minutes
            
            # Handle minute underflow
            if notify_minute < 0:
                notify_minute += 60
                notify_hour -= 1
                if notify_hour < 0:
                    notify_hour = 23
            
            # Create job ID
            job_id = f"meal_{user_id}_{meal_name.replace(' ', '_')}_{meal_time.replace(':', '').replace(' ', '')}"
            
            # Build notification content
            title = f"🍽️ {meal_name}"
            if meal_items and len(meal_items) > 0:
                items_preview = ", ".join(meal_items[:2])
                if len(meal_items) > 2:
                    items_preview += f" +{len(meal_items) - 2} more"
                body = f"Time for your meal! {items_preview}"
            else:
                body = f"It's almost {meal_time} - time for your scheduled meal!"
            
            # Schedule daily notification
            def send_notification():
                print(f"[Notifications] Sending reminder for {meal_name} to {len(tokens)} devices")
                for token in tokens:
                    send_push_notification(
                        token=token,
                        title=title,
                        body=body,
                        data={
                            "type": "meal_reminder",
                            "meal_name": meal_name,
                            "meal_time": meal_time,
                            "user_id": user_id
                        }
                    )
            
            # Remove existing job if any
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass
            
            # Add new job - runs daily at specified time
            # Add new job - runs daily at specified time
            self.scheduler.add_job(
                send_notification,
                trigger=CronTrigger(hour=notify_hour, minute=notify_minute),
                id=job_id,
                name=f"Meal Reminder: {meal_name}",
                replace_existing=True,
                misfire_grace_time=3600  # Fire if missed within last hour (e.g. server restart)
            )
            
            self._log(f"Scheduled '{meal_name}' for user {user_id} at {notify_hour:02d}:{notify_minute:02d} (lead time: {lead_time_minutes}min)")
            
            # CATCH-UP LOGIC: Check if we just missed this today and fire immediately
            now = datetime.now(self.timezone)
            # Create a target time for today
            today_target = now.replace(hour=notify_hour, minute=notify_minute, second=0, microsecond=0)
            
            # If target was in the last hour, fire immediately
            time_diff = (now - today_target).total_seconds()
            if 0 <= time_diff < 3600:
                print(f"[Notifications] Catch-up: Missed schedule for '{meal_name}' by {int(time_diff/60)} mins. Sending now.")
                # Run purely inside a try-catch to avoid blocking startup
                try:
                    send_notification()
                except Exception as e:
                    print(f"[Notifications] Catch-up error: {e}")
            
            return job_id
            
        except Exception as e:
            print(f"[Notifications] Scheduling error: {e}")
            return None
    
    def schedule_from_diet_plan(
        self,
        user_id: str,
        diet_plan: Dict[str, Any],
        tokens: List[str],
        lead_time_minutes: int = 5,
        custom_timings: Dict[str, str] = None
    ) -> List[str]:
        """
        Schedule all meal notifications from a diet plan.
        
        Args:
            user_id: User identifier
            diet_plan: Diet plan data from AI service
            tokens: List of FCM device tokens
            lead_time_minutes: Minutes before meal time to notify
            custom_timings: Optional dict of {meal_name: custom_time} overrides
        
        Returns:
            List of scheduled job IDs
        """
        job_ids = []
        custom_timings = custom_timings or {}
        
        # Get meals from diet protocol
        diet_protocol = diet_plan.get('diet_protocol', {})
        meals = diet_protocol.get('meals', [])
        
        if not meals:
            print(f"[Notifications] No meals found in diet plan for user {user_id}")
            return job_ids
        
        print(f"[Notifications] Scheduling {len(meals)} meal reminders for user {user_id}")
        
        for meal in meals:
            meal_name = meal.get('name', 'Meal')
            # Check for custom timing override
            meal_time = custom_timings.get(meal_name) or meal.get('time', '')
            meal_items = meal.get('bullets', [])
            
            if meal_time:
                job_id = self.schedule_meal_reminder(
                    user_id=user_id,
                    meal_name=meal_name,
                    meal_time=meal_time,
                    tokens=tokens,
                    lead_time_minutes=lead_time_minutes,
                    meal_items=meal_items
                )
                
                if job_id:
                    job_ids.append(job_id)
        
        return job_ids
    
    def cancel_user_notifications(self, user_id: str) -> int:
        """
        Cancel all scheduled notifications for a user.
        
        Returns:
            Number of jobs cancelled
        """
        if not self.scheduler:
            return 0
        
        cancelled = 0
        prefix = f"meal_{user_id}_"
        
        for job in self.scheduler.get_jobs():
            if job.id.startswith(prefix):
                self.scheduler.remove_job(job.id)
                cancelled += 1
        
        print(f"[Notifications] Cancelled {cancelled} notifications for user {user_id}")
        return cancelled
    
    def get_user_jobs(self, user_id: str) -> List[Dict]:
        """Get all scheduled jobs for a user."""
        if not self.scheduler:
            return []
        
        prefix = f"meal_{user_id}_"
        jobs = []
        
        for job in self.scheduler.get_jobs():
            if job.id.startswith(prefix):
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None
                })
        
        return jobs
    
    def send_test_notification(self, token: str) -> bool:
        """Send a test notification to verify setup."""
        return send_push_notification(
            token=token,
            title="🎉 DietNotify Test",
            body="Notifications are working! You'll receive meal reminders at scheduled times.",
            data={"type": "test"}
        )


# Global scheduler instance
_scheduler = None

def get_scheduler() -> NotificationScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = NotificationScheduler()
    return _scheduler

def init_notifications():
    """Initialize the notification system."""
    # Initialize Firebase
    firebase_ok = init_firebase()
    
    # Initialize Scheduler
    scheduler = get_scheduler()
    scheduler_ok = scheduler.start()
    
    # Restore jobs from DB
    restored_count = 0
    if scheduler_ok:
        restored_count = scheduler.restore_jobs()
    
    return {
        "firebase": firebase_ok,
        "scheduler": scheduler_ok,
        "restored_jobs": restored_count
    }
