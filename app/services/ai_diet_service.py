"""
AI Diet Service for DietNotify
Generates personalized diet plans using Google Gemini AI
Pattern adapted from crop flow ai for robust API handling
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    print("[DietAI] google-genai SDK loaded successfully")
except ImportError as e:
    print(f"[DietAI] google-genai library not found: {e}")
    print("[DietAI] Please run: pip install google-genai")
    genai = None
    types = None


# API KEY MANAGEMENT - Multiple keys for fallback
GEMINI_API_KEYS = [key.strip() for key in os.getenv('GEMINI_API_KEY', '').split(',') if key.strip()]


class APIKeyRotator:
    """Thread-safe API key rotation manager - adapted from crop flow ai."""
    def __init__(self, keys: List[str]):
        self.keys = [k for k in keys if k]
        self.current_index = 0
        self.failed_keys = set()
        
        if not self.keys:
            print("[DietAI] WARNING: No API keys available!")
    
    def get_current_key(self) -> Optional[str]:
        if not self.keys:
            return None
        return self.keys[self.current_index]
    
    def rotate_key(self) -> Optional[str]:
        if not self.keys:
            return None
            
        self.failed_keys.add(self.current_index)
        for _ in range(len(self.keys)):
            self.current_index = (self.current_index + 1) % len(self.keys)
            if self.current_index not in self.failed_keys:
                print(f"[DietAI] Rotated to API key #{self.current_index + 1}")
                return self.keys[self.current_index]
        
        print(f"[DietAI] All keys exhausted, resetting rotation")
        self.failed_keys.clear()
        return self.keys[self.current_index]
    
    def reset_failures(self):
        self.failed_keys.clear()


# Global API key rotator
api_rotator = APIKeyRotator(GEMINI_API_KEYS)


class DietAI:
    """
    AI-powered diet plan generator using Google Gemini.
    Uses robust error handling and API key rotation.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or api_rotator.get_current_key()
        self.client = None
        self.model_name = "gemini-2.5-flash"
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini API client."""
        if not self.api_key:
            print("[DietAI] No API Key provided!")
            return
        
        if not genai:
            print("[DietAI] google-genai SDK not available!")
            return
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            print(f"[DietAI] Gemini Client initialized with model: {self.model_name}")
        except Exception as e:
            print(f"[DietAI] Error initializing client: {e}")
            self.client = None
    
    def _get_system_prompt(self) -> str:
        """
        CRITICAL: This prompt generates the EXACT JSON structure required by dashboard.
        All arrays must be NUMERIC - not placeholder text.
        All labels must MATCH the dashboard JavaScript expectations.
        """
        return """You are an elite sports nutritionist and bio-physicist creating a comprehensive, scientific diet protocol.

=== ABSOLUTE CRITICAL RULES ===
1. Output ONLY valid JSON - no markdown, no text before or after
2. ALL numeric arrays MUST contain REAL NUMBERS, not placeholders like "<number>" or "X"
3. All chart data arrays MUST have the EXACT number of elements shown
4. Calculate real values based on user's weight, height, age, gender, activity level, and goal
5. NO PARAGRAPHS in text fields - use bullet points (max 12 words each)
6. Meal plans must be realistic, varied, and culturally appropriate

=== EXACT JSON OUTPUT STRUCTURE ===
{
    "user_overview": {
        "bmi": <calculated BMI as decimal, e.g., 22.5>,
        "daily_calories_target": <calculated TDEE as integer, e.g., 2200>,
        "protein_target_g": <calculated protein as integer, e.g., 140>,
        "carbs_target_g": <calculated carbs as integer, e.g., 280>,
        "fat_target_g": <calculated fat as integer, e.g., 75>,
        "fiber_target_g": <recommended fiber as integer, e.g., 35>,
        "water_target_l": <recommended water as decimal, e.g., 3.0>
    },
    
    "metabolic_logic_flow": [
        {"phase": "Stimulus", "trigger": "Morning cortisol peaks naturally", "process": "Body mobilizes stored glycogen", "outcome": "Primed for nutrient absorption"},
        {"phase": "Assimilation", "trigger": "Post-meal insulin response", "process": "Nutrients shuttled to muscles", "outcome": "Optimal protein synthesis"},
        {"phase": "Performance", "trigger": "Steady blood glucose levels", "process": "Mitochondrial ATP production", "outcome": "Sustained mental clarity"}
    ],

    "bio_analysis": {
        "strengths": [
            {"icon": "💪", "title": "Metabolic Advantage", "points": ["Young metabolism supports fat oxidation", "Responds well to protein intake", "Good recovery potential"]},
            {"icon": "⚡", "title": "Activity Synergy", "points": ["Daily movement supports calorie burn", "Built-in cardiovascular base"]}
        ],
        "weaknesses": [
            {"icon": "⚠️", "title": "Nutritional Gaps", "points": ["May lack essential micronutrients", "Hydration needs attention"]},
            {"icon": "🔻", "title": "Metabolic Risks", "points": ["Blood sugar fluctuations possible", "Sleep quality impacts recovery"]}
        ],
        "macro_breakdown": {
            "labels": ["Protein", "Complex Carbs", "Fibrous Carbs", "Healthy Fats", "Saturated Fats"],
            "values": [25, 35, 10, 25, 5],
            "colors": ["#00ff88", "#00d4ff", "#7c3aed", "#ff6b6b", "#ffd93d"]
        },
        "key_nutrients": [
            {"name": "Vitamin D3", "points": ["Critical for calcium absorption", "Supports immune function"], "source": "Fortified milk, sunlight", "priority": "HIGH"},
            {"name": "Omega-3 DHA", "points": ["Brain cell membrane health", "Reduces inflammation"], "source": "Fatty fish, walnuts", "priority": "HIGH"},
            {"name": "Magnesium", "points": ["Muscle recovery essential", "Sleep quality optimizer"], "source": "Dark greens, nuts", "priority": "MEDIUM"}
        ],
        "avoid_foods": [
            {"food": "Refined Sugar", "reasons": ["Spikes blood glucose rapidly", "Creates energy crashes"], "swap": "Natural honey in moderation"},
            {"food": "Processed Oils", "reasons": ["Pro-inflammatory effects", "Poor omega ratio"], "swap": "Extra virgin olive oil"},
            {"food": "Excessive Sodium", "reasons": ["Water retention issues", "Blood pressure impact"], "swap": "Herbs and natural spices"}
        ]
    },
    
    "quick_tips": [
        {"icon": "💧", "tip": "Drink 500ml water immediately upon waking"},
        {"icon": "🏋️", "tip": "Time protein intake within 30min post-workout"},
        {"icon": "🌙", "tip": "Avoid screens 1 hour before sleep for better recovery"},
        {"icon": "🍽️", "tip": "Chew each bite 20 times for optimal digestion"}
    ],
    
    "diet_protocol": {
        "strategy_points": [
            "Front-load calories earlier in the day for metabolism",
            "Include protein source in every meal for satiety",
            "Complex carbs fuel workouts and recovery",
            "Strategic fiber timing prevents bloating"
        ],
        "daily_schedule": {
            "labels": ["6AM", "9AM", "12PM", "3PM", "6PM", "9PM"],
            "activity": ["Wake", "Work", "Peak Energy", "Refuel", "Dinner", "Wind Down"],
            "energy_level": [30, 70, 90, 65, 80, 40]
        },
        "meal_calories_chart": {
            "labels": ["Breakfast", "AM Snack", "Lunch", "PM Snack", "Dinner"],
            "values": [450, 180, 550, 160, 500],
            "colors": ["#00ff88", "#00d4ff", "#7c3aed", "#ff6b6b", "#ffd93d"]
        },
        "meals": [
            {
                "time": "7:00 AM",
                "name": "Metabolic Ignition Breakfast",
                "macros": {"P": 35, "C": 45, "F": 15},
                "bullets": ["3 whole eggs scrambled", "2 slices whole grain toast", "1/2 avocado", "1 cup mixed berries"],
                "science_logic": ["Protein triggers thermogenesis", "Complex carbs fuel morning cortisol"]
            },
            {
                "time": "10:30 AM",
                "name": "Anabolic Snack",
                "macros": {"P": 20, "C": 15, "F": 10},
                "bullets": ["Greek yogurt 150g", "Handful almonds", "Honey drizzle"],
                "science_logic": ["Casein protein sustains amino acid levels", "Healthy fats slow digestion"]
            },
            {
                "time": "1:00 PM",
                "name": "Performance Fuel Lunch",
                "macros": {"P": 45, "C": 60, "F": 20},
                "bullets": ["Grilled chicken 200g", "Brown rice 1 cup", "Steamed broccoli", "Olive oil drizzle"],
                "science_logic": ["Peak insulin sensitivity at midday", "Fiber prevents afternoon crash"]
            },
            {
                "time": "4:30 PM",
                "name": "Pre-Workout Boost",
                "macros": {"P": 15, "C": 30, "F": 5},
                "bullets": ["Banana with peanut butter", "Green tea"],
                "science_logic": ["Fast carbs prepare glycogen stores", "Caffeine enhances focus"]
            },
            {
                "time": "7:30 PM",
                "name": "Recovery Dinner",
                "macros": {"P": 40, "C": 40, "F": 25},
                "bullets": ["Salmon fillet 180g", "Quinoa 1 cup", "Roasted vegetables", "Lemon herb dressing"],
                "science_logic": ["Omega-3s reduce exercise inflammation", "Moderate carbs support sleep quality"]
            }
        ]
    },

    "supplement_protocol": [
        {"name": "Vitamin D3", "dosage": "2000 IU daily with breakfast", "bullets": ["Essential in low-sun climates", "Supports immune and bone health"]},
        {"name": "Omega-3 Fish Oil", "dosage": "2g EPA/DHA daily", "bullets": ["Anti-inflammatory for joints", "Cognitive function support"]},
        {"name": "Magnesium Glycinate", "dosage": "400mg before bed", "bullets": ["Promotes relaxation and sleep", "Prevents muscle cramps"]}
    ],
    
    "performance_projection": {
        "health_radar": {
            "categories": ["Energy", "Digestion", "Sleep", "Strength", "Recovery", "Focus"],
            "current": [5, 4, 5, 4, 4, 5],
            "projected": [8, 7, 8, 7, 8, 8]
        },
        "week_by_week": {
            "labels": ["W1", "W2", "W3", "W4"],
            "energy_index": [55, 65, 78, 88],
            "cognitive_clarity": [50, 62, 75, 85],
            "hormonal_balance": [45, 58, 72, 82],
            "fat_loss_kg": [0.3, 0.8, 1.5, 2.2],
            "muscle_gain_kg": [0.1, 0.2, 0.4, 0.6]
        },
        "milestones": [
            {"week": 1, "points": ["Initial metabolic reset begins", "Hydration levels stabilize"]},
            {"week": 2, "points": ["Energy levels noticeably improve", "Digestion becomes regular"]},
            {"week": 3, "points": ["Body composition changes visible", "Recovery time shortened"]},
            {"week": 4, "points": ["Full metabolic adaptation achieved", "Sustainable habits formed"]}
        ]
    },
    
    "expert_notes": [
        "Track morning weight weekly for consistent progress data",
        "Adjust portions based on hunger and activity levels",
        "Sleep 7-9 hours - this is when hormones repair muscle"
    ],
    
    "reasoning_signature": "• Caloric targets calculated via Mifflin-St Jeor equation\\n• Macro split optimized for body recomposition\\n• Meal timing aligned with circadian rhythm\\n• Nutrient density prioritized over calorie counting"
}

=== CUSTOMIZATION REQUIREMENTS ===
1. CALCULATE actual BMI from user's height and weight
2. CALCULATE actual TDEE based on activity level and goal (deficit for fat loss, surplus for muscle gain)
3. CUSTOMIZE meals based on dietary preferences (vegetarian, vegan, etc.)
4. AVOID foods listed in user's allergies
5. RESPECT cuisine preferences in meal suggestions
6. ADJUST all chart values to reflect the user's specific situation
7. The week_by_week projections should be REALISTIC for the user's goal and starting point"""
    
    def _build_user_prompt(self, user_profile: Dict[str, Any], duration: str) -> str:
        """Build the user prompt from profile data."""
        # Map keys from frontend/database to AI prompt
        activity = user_profile.get('job_activity') or user_profile.get('activity_level') or "Moderate"
        diet_pref = user_profile.get('diet_type') or user_profile.get('dietary_preferences') or "No specific preference"
        medical = user_profile.get('conditions') or "No specific conditions"
        allergies = user_profile.get('allergies') or "No specific allergies"
        cuisine = user_profile.get('cuisine') or "Global/Mixed"
        
        # Calculate basic metrics for the AI
        weight = float(user_profile.get('weight', 70))
        height = float(user_profile.get('height', 170))
        age = int(user_profile.get('age', 25))
        gender = user_profile.get('gender', 'Male')
        
        # Calculate BMI for reference
        bmi = weight / ((height / 100) ** 2)
        
        return f"""
=== USER PROFILE FOR DIET PLAN GENERATION ===

**BIOMETRIC DATA:**
- Name: {user_profile.get('name', 'User')}
- Age: {age} years
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Pre-calculated BMI: {bmi:.1f}
- Activity Level: {activity}
- Primary Goal: {user_profile.get('goal', 'General Health')}

**DIETARY CONTEXT:**
- Dietary Philosophy: {diet_pref}
- Preferred Cuisine: {cuisine}
- Health Conditions: {medical}
- Allergies/Intolerances: {allergies}

**PLAN PARAMETERS:**
- Duration: {duration}
- Output Format: Complete JSON protocol (NO markdown, NO text wrapping)

**GENERATION INSTRUCTIONS:**
1. CALCULATE exact TDEE for this user using Mifflin-St Jeor formula
2. ADJUST caloric target based on goal (deficit for weight loss, surplus for muscle gain)
3. CREATE meals that respect dietary preferences and allergies
4. GENERATE realistic numeric projections for all charts
5. ENSURE all array lengths match exactly what is specified in the schema
6. DO NOT use placeholder values - calculate everything based on user data

Generate the complete JSON protocol now:"""
    
    def generate_comprehensive_plan(self, user_profile: Dict[str, Any], duration: str = "weekly") -> Dict[str, Any]:
        """
        Generates EVERYTHING in ONE single API call.
        Uses API key rotation for robustness.
        """
        if not self.client:
            print("[DietAI] No client available, attempting to reinitialize...")
            self._initialize_client()
            if not self.client:
                return {"error": "AI Service unavailable - could not initialize client"}
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(user_profile, duration)
        
        # Try with API key rotation on failure
        max_attempts = len(GEMINI_API_KEYS)
        
        for attempt in range(max_attempts):
            try:
                print(f"[DietAI] Attempt {attempt + 1}/{max_attempts} - Generating plan with {self.model_name}...")
                print(f"[DietAI] User: {user_profile.get('name', 'Unknown')}, Goal: {user_profile.get('goal', 'Unknown')}")
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        max_output_tokens=30000,
                        temperature=0.7
                    )
                )
                
                print(f"[DietAI] Response received! Size: {len(response.text)} chars")
                
                # Clean and parse response
                clean_text = response.text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                result = json.loads(clean_text)
                
                # Add metadata
                result['_ai_generated'] = True
                result['_model'] = self.model_name
                result['_timestamp'] = datetime.now().isoformat()
                result['_user_name'] = user_profile.get('name', 'User')
                
                print(f"[DietAI] Successfully generated plan for {user_profile.get('name', 'User')}!")
                api_rotator.reset_failures()
                return result
                
            except json.JSONDecodeError as e:
                print(f"[DietAI] JSON Parse Error (attempt {attempt + 1}): {e}")
                print(f"[DietAI] Raw response preview: {response.text[:500] if response else 'No response'}...")
                
            except Exception as e:
                error_str = str(e).lower()
                print(f"[DietAI] API Error (attempt {attempt + 1}): {e}")
                
                if any(x in error_str for x in ['quota', 'rate', 'resource', '429', 'exhausted']):
                    print(f"[DietAI] Rate limit detected, rotating API key...")
                    self.api_key = api_rotator.rotate_key()
                    self._initialize_client()
                else:
                    print(f"[DietAI] Unknown error, rotating API key for resilience...")
                    self.api_key = api_rotator.rotate_key()
                    self._initialize_client()
        
        print(f"[DietAI] All {max_attempts} attempts failed!")
        return {
            "error": "AI Generation Failed after all attempts",
            "details": "Please check server logs for details"
        }
    def search_experts(self, query: str, location_context: str) -> List[Dict[str, Any]]:
        """
        Uses Gemini 2.5 Flash Lite with API key rotation to find real health experts.
        """
        if not self.client:
            self._initialize_client()
            if not self.client:
                return []

        search_model = "gemini-2.5-flash-lite"
        max_attempts = len(GEMINI_API_KEYS)
        
        system_prompt = """You are a health discovery assistant. 
        Your task is to find REAL, REPUTABLE health experts, nutritionists, dietitians, and clinics near a specific location.
        Return ONLY a JSON array of objects.
        Each object MUST have:
        - "name": Full name of the expert or clinic
        - "address": Real-world physical address
        - "type": (Nutritionist, Dietitian, Clinic, Specialist)
        - "relevance": Why you are suggesting them (1 sentence)
        - "id": a unique string ID
        """

        prompt = f"Search for real {query} near {location_context}. Return 5 results as JSON."

        for attempt in range(max_attempts):
            try:
                print(f"[DietAI] AI Discovery (Attempt {attempt+1}) using {search_model} for: {location_context}")
                response = self.client.models.generate_content(
                    model=search_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json"
                    )
                )
                
                print(f"[DietAI] AI Discovery Success!")
                experts = json.loads(response.text.strip())
                return experts if isinstance(experts, list) else []
                
            except Exception as e:
                print(f"[DietAI] AI Discovery attempt {attempt+1} failed: {e}")
                self.api_key = api_rotator.rotate_key()
                self._initialize_client()
                
        return []
    def chat_with_assistant(self, message: str, user_profile: Dict[str, Any]) -> str:
        """
        Diety AI Assistant - Using Gemma 3 4B for smart, concise health chat.
        """
        if not self.client:
            self._initialize_client()
            if not self.client:
                return "I'm sorry, I'm currently disconnected."

        assistant_model = "gemma-3-4b-it"
        
        system_prompt = f"""You are 'Diety', a smart, friendly health assistant for the DietNotify platform.
        Current User: {user_profile.get('name', 'User')}
        Goal: {user_profile.get('goal', 'Health Improvement')}
        
        RULES:
        1. Keep responses extremely concise (1-3 lines max).
        2. Be smart, encouraging, and medically grounded but conversational.
        3. Never give dangerous medical advice - suggest consulting a professional if needed.
        4. Focus on nutrition, exercise, and wellness.
        """

        # Gemma 3 does not support a separate 'system' role. 
        # We merge instructions into the user prompt.
        full_prompt = f"INSTRUCTIONS:\n{system_prompt}\n\nUSER MESSAGE:\n{message}"

        try:
            print(f"[Diety] Chatting with Gemma 3 4B-IT for: {user_profile.get('name', 'User')}")
            response = self.client.models.generate_content(
                model=assistant_model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=250,
                    temperature=0.8
                )
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"[Diety] Chat error: {e}")
            return "I'm having a small metabolic glitch. Can we try again in a moment?"
