"""
Database Module for DietNotify
Simple User ID + Password Authentication with Supabase
"""
import os
import hashlib
import requests
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://irgaogiswwgysrnqgxnw.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlyZ2FvZ2lzd3dneXNybnFneG53Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4Mzg0NTIsImV4cCI6MjA4NTQxNDQ1Mn0.yjORsAZ46qlSYl-dzz24YIH_j8XT-EF34B72J4gVdqo')

print(f"[Supabase] Connected to {SUPABASE_URL}")


def init_database():
    """Initialize/verify database connection - called during app startup"""
    try:
        # Test connection by making a simple request
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=get_headers(),
            params={"limit": "1"}
        )
        if response.status_code == 200:
            print("[Supabase] Database connection verified successfully")
            return True
        else:
            print(f"[Supabase] Database connection test returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"[Supabase] Database initialization error: {e}")
        return False


def get_headers():
    """Get Supabase API headers"""
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


# ============== USER OPERATIONS ==============
def get_user_by_id(user_id: str) -> dict:
    """Get user by user_id"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}", "limit": "1"}
        )
        
        if response.status_code == 200:
            users = response.json()
            return users[0] if users else None
        return None
    except Exception as e:
        print(f"[Supabase] Get user error: {e}")
        return None


def create_user(user_id: str, password: str) -> dict:
    """Create a new user with hashed password"""
    user_data = {
        "user_id": user_id,
        "password_hash": hash_password(password),
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=get_headers(),
            json=user_data
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"[Supabase] User created: {user_id}")
            return result[0] if result else user_data
        else:
            print(f"[Supabase] Create user error: {response.text}")
            return None
    except Exception as e:
        print(f"[Supabase] Create user exception: {e}")
        return None


def authenticate_user(user_id: str, password: str) -> dict:
    """Authenticate user with user_id and password"""
    user = get_user_by_id(user_id)
    
    if user:
        password_hash = hash_password(password)
        if user.get('password_hash') == password_hash:
            return user
    
    return None


# ============== PROFILE OPERATIONS ==============
def get_profile(user_id: str) -> dict:
    """Get user profile by user_id"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}", "limit": "1"}
        )
        
        if response.status_code == 200:
            profiles = response.json()
            return profiles[0] if profiles else None
        return None
    except Exception as e:
        print(f"[Supabase] Get profile error: {e}")
        return None


def save_profile_step(user_id: str, step: int, step_data: dict) -> dict:
    """Save profile data for a specific step (auto-save)"""
    existing = get_profile(user_id)
    
    if existing:
        # Merge with existing data
        profile_data = existing.copy()
        for key in ['id', 'created_at']:
            profile_data.pop(key, None)
    else:
        profile_data = {"user_id": user_id}
    
    # Update with new step data
    profile_data.update(step_data)
    profile_data['current_step'] = step
    profile_data['is_complete'] = (step >= 5)
    profile_data['updated_at'] = datetime.utcnow().isoformat()
    
    try:
        if existing:
            # Update
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers=get_headers(),
                params={"user_id": f"eq.{user_id}"},
                json=profile_data
            )
        else:
            # Insert
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers=get_headers(),
                json=profile_data
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"[Supabase] Profile step {step} saved for: {user_id}")
            return result[0] if result else profile_data
        else:
            print(f"[Supabase] Save profile error: {response.text}")
            return None
    except Exception as e:
        print(f"[Supabase] Profile save exception: {e}")
        return None


def get_profile_progress(user_id: str) -> dict:
    """Get profile completion progress"""
    profile = get_profile(user_id)
    if profile:
        return {
            "has_profile": True,
            "current_step": profile.get('current_step', 1),
            "is_complete": profile.get('is_complete', False),
            "profile": profile
        }
    return {
        "has_profile": False,
        "current_step": 1,
        "is_complete": False,
        "profile": None
    }


# ============== DIET PLAN OPERATIONS ==============
def save_diet_plan(user_id: str, plan_data: dict, duration_type: str = 'weekly') -> dict:
    """Save a generated diet plan"""
    plan_record = {
        "user_id": user_id,
        "duration_type": duration_type,
        "plan_data": plan_data,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Deactivate existing active plans
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}", "is_active": "eq.true"},
            json={"is_active": False}
        )
        
        # Save new plan
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            json=plan_record
        )
        
        if response.status_code == 201:
            result = response.json()
            return result[0] if result else plan_record
        else:
            print(f"[Supabase] Save plan error: {response.text}")
            return None
    except Exception as e:
        print(f"[Supabase] Plan save exception: {e}")
        return None


def get_user_plans(user_id: str, limit: int = 10) -> list:
    """Get user's diet plans"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            params={
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
                "limit": str(limit)
            }
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"[Supabase] Get plans error: {e}")
        return []


def get_active_plan(user_id: str) -> dict:
    """Get user's active diet plan"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            params={
                "user_id": f"eq.{user_id}",
                "is_active": "eq.true",
                "limit": "1"
            }
        )
        
        if response.status_code == 200:
            plans = response.json()
            return plans[0] if plans else None
        return None
    except Exception as e:
        print(f"[Supabase] Get active plan error: {e}")
        return None


def get_plan_by_id(plan_id: str) -> dict:
    """Get diet plan by ID"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            params={"id": f"eq.{plan_id}", "limit": "1"}
        )
        
        if response.status_code == 200:
            plans = response.json()
            return plans[0] if plans else None
        return None
    except Exception as e:
        print(f"[Supabase] Get plan error: {e}")
        return None


def set_active_plan(user_id: str, plan_id: str) -> bool:
    """Set a specific plan as active"""
    try:
        # Deactivate all plans
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            params={"user_id": f"eq.{user_id}"},
            json={"is_active": False}
        )
        
        # Activate specific plan
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/diet_plans",
            headers=get_headers(),
            params={"id": f"eq.{plan_id}", "user_id": f"eq.{user_id}"},
            json={"is_active": True}
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"[Supabase] Set active plan error: {e}")
        return False


# ============== ADMIN OPERATIONS ==============
def clear_all_data() -> bool:
    """Clear all data from tables (admin only)"""
    try:
        for table in ['users', 'profiles', 'diet_plans']:
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers=get_headers(),
                params={"id": "neq.0"}  # Delete all
            )
        print("[Supabase] All data cleared")
        return True
    except Exception as e:
        print(f"[Supabase] Clear data error: {e}")
        return False
