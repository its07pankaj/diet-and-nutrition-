from flask import Blueprint, render_template, request, jsonify, session, redirect
from .services.ai_diet_service import DietAI
from .core.database import (
    get_profile, save_diet_plan, get_user_plans, 
    get_active_plan, get_plan_by_id, set_active_plan,
    get_profile_progress
)
import os

diet_bp = Blueprint('diet', __name__)

# Initialize AI Service
API_KEY = os.getenv('GEMINI_API_KEY', '').split(',')[0]
ai_service = DietAI(api_key=API_KEY)


def is_authenticated():
    return 'user_id' in session


def get_current_user():
    return session.get('user_id')


@diet_bp.route('/diet')
def diet_smart_entry():
    """Smart Entry Point: Redirects based on user state"""
    if not is_authenticated():
        return redirect('/login')
    
    user_id = get_current_user()
    
    # 1. Check Profile Completion
    progress = get_profile_progress(user_id)
    if not progress['is_complete']:
        # Force redirect to profile if incomplete
        return redirect('/profile_setup.html')
    
    # 2. Check for Active Plan
    active_plan = get_active_plan(user_id)
    if active_plan:
        return redirect('/diet/dashboard')
    else:
        return redirect('/diet/create')


@diet_bp.route('/diet/create')
def create_plan_page():
    """Diet plan creation page (Generator)"""
    if not is_authenticated():
        return redirect('/login')
        
    # Enforce profile completion even here
    user_id = get_current_user()
    progress = get_profile_progress(user_id)
    if not progress['is_complete']:
         return redirect('/profile_setup.html')

    return render_template('diet_create.html')


@diet_bp.route('/diet/dashboard')
def dashboard_page():
    """Diet dashboard page (Results)"""
    if not is_authenticated():
        return redirect('/login')
    
    # Dashboard should handle "No Plan" gracefully (maybe show "Create One" empty state)
    # But strictly speaking, if we use the smart router, we land here only if plan exists.
    # However, for direct access, we'll allow it but templates should handle data.
    return render_template('diet_dashboard.html')


@diet_bp.route('/api/diet/active_plan', methods=['GET'])
def get_active_plan_api():
    """Get user's currently active diet plan"""
    if not is_authenticated():
        return jsonify({"error": "Login required"}), 401
    
    user_id = get_current_user()
    plan = get_active_plan(user_id)
    
    if plan and plan.get('plan_data'):
        return jsonify({
            "status": "success",
            "plan_data": plan['plan_data'],
            "plan_meta": {
                "id": plan.get('id'),
                "created_at": plan.get('created_at'),
                "duration_type": plan.get('duration_type')
            }
        })
    
    return jsonify({"status": "no_plan", "message": "No active plan found"})


@diet_bp.route('/api/diet/user_profile', methods=['GET'])
def get_user_profile():
    """Get current user's profile for diet planning"""
    if not is_authenticated():
        return jsonify({"error": "Login required", "authenticated": False}), 401
    
    user_id = get_current_user()
    profile = get_profile(user_id)
    
    if not profile:
        return jsonify({
            "authenticated": True,
            "has_profile": False,
            "message": "Please complete your profile first"
        })
    
    return jsonify({
        "authenticated": True,
        "has_profile": True,
        "profile": profile
    })


@diet_bp.route('/api/diet/generate_all', methods=['POST'])
def generate_all():
    """
    Generates EVERYTHING (Analysis + Plan) in one go.
    Now fetches profile from database if user is authenticated.
    """
    try:
        data = request.json or {}
        duration = data.get('duration', 'weekly')
        
        # Check if user is authenticated and has profile
        if is_authenticated():
            user_id = get_current_user()
            profile = get_profile(user_id)
            if profile:
                # Remove Supabase-specific fields
                user_profile = {k: v for k, v in profile.items() if k not in ['id', 'email', 'updated_at', 'created_at', 'current_step', 'is_complete']}
                print(f"[DietRoutes] Using profile from database for: {user_id}")
            else:
                return jsonify({"error": "Profile not found. Please complete your profile first."}), 400
        else:
            # Fallback: use profile from request (for unauthenticated users or testing)
            user_profile = data.get('profile', {})
            if not user_profile:
                return jsonify({"error": "Login required or provide profile data"}), 400
        
        print(f"[DietRoutes] Generating comprehensive {duration} plan for:", user_profile)
        result = ai_service.generate_comprehensive_plan(user_profile, duration)
        
        # Add duration type to result for saving
        result['duration_type'] = duration
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[DietRoutes] Error: {e}")
        return jsonify({"error": str(e)}), 500


@diet_bp.route('/api/diet/save_plan', methods=['POST'])
def save_plan():
    """Save generated diet plan to database"""
    if not is_authenticated():
        return jsonify({"error": "Login required"}), 401
    
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No plan data provided"}), 400
        
        user_id = get_current_user()
        duration_type = data.get('duration_type', 'weekly')
        plan_data = data.get('plan_data', data)  # Allow full data or nested plan_data
        
        saved_plan = save_diet_plan(user_id, plan_data, duration_type)
        
        if saved_plan:
            return jsonify({
                "success": True,
                "message": "Plan saved successfully",
                "plan_id": saved_plan.get('id')
            })
        else:
            return jsonify({"error": "Failed to save plan"}), 500
        
    except Exception as e:
        print(f"[DietRoutes] Save plan error: {e}")
        return jsonify({"error": str(e)}), 500


@diet_bp.route('/api/diet/my_plans', methods=['GET'])
def my_plans():
    """Get all saved plans for current user"""
    if not is_authenticated():
        return jsonify({"error": "Login required", "authenticated": False}), 401
    
    try:
        user_id = get_current_user()
        limit = request.args.get('limit', 10, type=int)
        plans = get_user_plans(user_id, limit=limit)
        
        # Simplify plan data for listing (don't send full plan_data)
        plan_list = []
        for plan in plans:
            plan_list.append({
                "id": plan.get('id'),
                "duration_type": plan.get('duration_type'),
                "is_active": plan.get('is_active'),
                "created_at": plan.get('created_at'),
                # Include summary info if available
                "bio_summary": (plan.get('plan_data') or {}).get('bio_analysis', {}).get('body_type', 'N/A')
            })
        
        return jsonify({
            "authenticated": True,
            "plans": plan_list,
            "count": len(plan_list)
        })
        
    except Exception as e:
        print(f"[DietRoutes] Get plans error: {e}")
        return jsonify({"error": str(e)}), 500


@diet_bp.route('/api/diet/plan/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get specific plan by ID"""
    if not is_authenticated():
        return jsonify({"error": "Login required"}), 401
    
    try:
        plan = get_plan_by_id(plan_id)
        
        if not plan:
            return jsonify({"error": "Plan not found"}), 404
        
        # Verify ownership
        user_id = get_current_user()
        if plan.get('user_id') != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify({
            "success": True,
            "plan": plan
        })
        
    except Exception as e:
        print(f"[DietRoutes] Get plan error: {e}")
        return jsonify({"error": str(e)}), 500


@diet_bp.route('/api/diet/set_active/<plan_id>', methods=['POST'])
def set_active(plan_id):
    """Set a specific plan as active"""
    if not is_authenticated():
        return jsonify({"error": "Login required"}), 401
    
    try:
        user_id = get_current_user()
        success = set_active_plan(user_id, plan_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Plan set as active"
            })
        else:
            return jsonify({"error": "Plan not found or access denied"}), 404
            
    except Exception as e:
        print(f"[DietRoutes] Set active error: {e}")
        return jsonify({"error": str(e)}), 500
@diet_bp.route('/api/expert_search', methods=['POST'])
def expert_search():
    """AI-powered expert search near a location"""
    try:
        data = request.json or {}
        lat = data.get('lat')
        lng = data.get('lng')
        query = data.get('query', 'nutritionists and dietitians')
        location_name = data.get('location_name', f"coordinates {lat}, {lng}")

        if not lat or not lng:
            return jsonify({"error": "Location data missing"}), 400

        print(f"[DietRoutes] AI Search request for: {query} near {location_name}")
        experts = ai_service.search_experts(query, location_name)
        
        return jsonify({
            "status": "success",
            "experts": experts
        })
        
    except Exception as e:
        print(f"[DietRoutes] Expert search error: {e}")
        return jsonify({"error": str(e)}), 500
@diet_bp.route('/api/assistant_chat', methods=['POST'])
def assistant_chat():
    """Endpoint for Diety AI Assistant (Gemma 3)"""
    print("[DietRoutes] Incoming assistant chat request...")
    if not is_authenticated():
        print("[DietRoutes] Chat failed: User not authenticated")
        return jsonify({"error": "Login required"}), 401
        
    try:
        user_id = get_current_user()
        data = request.json or {}
        message = data.get('message')
        
        print(f"[DietRoutes] Message from user {user_id}: {message}")
        if not message:
            return jsonify({"error": "Message missing"}), 400
            
        # Get profile for context
        profile = get_profile(user_id)
        
        answer = ai_service.chat_with_assistant(message, profile)
        print(f"[DietRoutes] Gemma 3 response: {answer[:50]}...")
        
        return jsonify({
            "status": "success",
            "reply": answer
        })
        
    except Exception as e:
        print(f"[DietRoutes] Assistant chat error: {e}")
        return jsonify({"error": str(e)}), 500
