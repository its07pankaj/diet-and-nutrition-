"""
Authentication Routes for DietNotify
Simple User ID + Password Authentication
"""
from flask import Blueprint, request, jsonify, session, redirect, render_template
from functools import wraps
from .core.database import (
    create_user, authenticate_user, get_user_by_id,
    get_profile, get_profile_progress, save_profile_step, clear_all_data
)
import os

auth_bp = Blueprint('auth', __name__)


# ============== SESSION HELPERS ==============
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Login required", "authenticated": False}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current user_id from session"""
    return session.get('user_id')


def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session


# ============== PAGE ROUTES ==============
@auth_bp.route('/login')
def login_page():
    """Serve login page"""
    return render_template('login.html')


@auth_bp.route('/profile_setup.html')
def profile_setup_page():
    """Serve profile setup page"""
    return render_template('profile_setup.html')


# ============== AUTH API ==============
@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Create new user account"""
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '')
    
    if not user_id or len(user_id) < 3:
        return jsonify({"error": "User ID must be at least 3 characters"}), 400
    
    if not password or len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    
    # Check if user already exists
    existing = get_user_by_id(user_id)
    if existing:
        return jsonify({"error": "User ID already taken. Please choose another."}), 400
    
    # Create user
    user = create_user(user_id, password)
    
    if user:
        # Auto-login after signup
        session['user_id'] = user_id
        session.permanent = True
        
        return jsonify({
            "success": True,
            "message": "Account created successfully!",
            "user_id": user_id,
            "redirect": "/profile_setup.html"
        })
    else:
        return jsonify({"error": "Failed to create account. Please try again."}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login with user_id and password"""
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '')
    
    if not user_id or not password:
        return jsonify({"error": "User ID and password are required"}), 400
    
    # Authenticate
    user = authenticate_user(user_id, password)
    
    if user:
        # Create session
        session['user_id'] = user_id
        session.permanent = True
        
        # Check profile status
        progress = get_profile_progress(user_id)
        
        if progress['is_complete']:
            redirect_url = '/diet'
        else:
            redirect_url = '/profile_setup.html'
        
        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user_id": user_id,
            "redirect": redirect_url,
            "is_complete": progress['is_complete']
        })
    else:
        return jsonify({"error": "Invalid user ID or password"}), 401


@auth_bp.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Get current auth status and profile progress"""
    if is_authenticated():
        user_id = get_current_user()
        progress = get_profile_progress(user_id)
        return jsonify({
            "authenticated": True,
            "user_id": user_id,
            "has_profile": progress['has_profile'],
            "is_complete": progress['is_complete'],
            "current_step": progress['current_step'],
            "profile": progress['profile']
        })
    
    return jsonify({
        "authenticated": False
    })


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


# ============== PROFILE API ==============
@auth_bp.route('/api/auth/profile/step', methods=['POST'])
def save_profile_step_api():
    """Save profile data for a specific step (auto-save)"""
    if not is_authenticated():
        return jsonify({"error": "Login required"}), 401
    
    data = request.json or {}
    step = data.get('step', 1)
    step_data = data.get('data', {})
    
    if not step_data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = get_current_user()
    result = save_profile_step(user_id, step, step_data)
    
    if result:
        return jsonify({
            "success": True,
            "message": f"Step {step} saved",
            "current_step": step,
            "is_complete": step >= 5
        })
    else:
        return jsonify({"error": "Failed to save profile step"}), 500


@auth_bp.route('/api/auth/profile/progress', methods=['GET'])
def get_profile_progress_api():
    """Get profile completion progress"""
    if not is_authenticated():
        return jsonify({"error": "Login required", "authenticated": False}), 401
    
    user_id = get_current_user()
    progress = get_profile_progress(user_id)
    
    return jsonify({
        "authenticated": True,
        "user_id": user_id,
        **progress
    })


# ============== ADMIN ==============
@auth_bp.route('/api/auth/clear_database', methods=['POST'])
def clear_database():
    """Clear all database data (admin)"""
    data = request.json or {}
    admin_key = data.get('admin_key', '')
    
    if admin_key != 'dietnotify-admin-2026':
        return jsonify({"error": "Unauthorized"}), 403
    
    success = clear_all_data()
    
    return jsonify({
        "success": success,
        "message": "Database cleared" if success else "Clear failed"
    })
