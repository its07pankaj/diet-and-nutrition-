from flask import Blueprint, request, jsonify, render_template, send_from_directory, redirect, current_app
import os
import json
from . import loader
from .core.nutrition_engine import calculate_meal_totals, get_major_nutrients, get_detailed_nutrients

main_bp = Blueprint('main', __name__)

# Helper to get data directory
def get_data_dir():
    # app/../data
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

# ============== FRONTEND ROUTES ==============

@main_bp.route('/')
@main_bp.route('/index.html')
def home():
    return render_template('index.html')

@main_bp.route('/nutrition')
@main_bp.route('/nutrition.html')
def nutrition():
    return render_template('nutrition.html')



# Static asset route is handled automatically by Flask for 'static' folder
# But if html files link to "assets/...", we might need a redirect or ensuring templates use valid paths.
# Since we moved "frontend/assets" to "app/static", a request to "/assets/..." will fail 
# unless we route it or change HTML. 
# Changing ALL HTML is risky right now. Let's add a compatibility route.

@main_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('static', filename)

# ============== API ROUTES ==============

@main_bp.route('/api/search', methods=['GET'])
def search_food():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    results = loader.search(query, limit=50)
    return jsonify(results)

@main_bp.route('/api/calculate', methods=['POST'])
def calculate_meal():
    data = request.json or {}
    items = data.get('items', [])
    totals = calculate_meal_totals(items)
    return jsonify(totals)

@main_bp.route('/api/food/<food_name>', methods=['GET'])
def get_food_detail(food_name):
    # Search precise
    data = loader.get_dataframe()
    item = data[data['food'].str.lower() == food_name.lower()]
    
    if item.empty:
        return jsonify({"error": "Food not found"}), 404
    
    # Return first match
    match = item.iloc[0].to_dict()
    
    return jsonify({
        "food": match.get('food'),
        "major_nutrients": get_major_nutrients(match),
        "detailed_nutrients": get_detailed_nutrients(match),
        "raw_data": match
    })

@main_bp.route('/api/save_profile', methods=['POST'])
def save_profile():
    try:
        profile_data = request.json
        if not profile_data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Save to data/users/user_profile.json
        users_dir = os.path.join(get_data_dir(), 'users')
        if not os.path.exists(users_dir):
            os.makedirs(users_dir)
            
        profile_path = os.path.join(users_dir, "user_profile.json")
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=4)
            
        return jsonify({"status": "success", "message": "Profile saved successfully"})
    except Exception as e:
        print(f"Error saving profile: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@main_bp.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "message": "DietNotify API v2 running",
        "total_foods": len(loader.get_dataframe()) if loader else 0
    })
