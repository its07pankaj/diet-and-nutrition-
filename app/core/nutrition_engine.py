"""
DietNotify - Scientific Calculations & Models
This file contains ONLY functions and classes for nutrition calculations.
NO SERVER CODE HERE - Use server.py to run the application.
"""

# ============== SCIENTIFIC NUTRIENT CALCULATIONS ==============

# Major nutrients to display prominently
MAJOR_NUTRIENTS = ['Caloric Value', 'Protein', 'Fat', 'Carbohydrates', 'Sugars']

# Keys to exclude from calculations (metadata, not nutritional)
EXCLUDE_KEYS = ['food', 'id', 'index', 'Unnamed: 0', 'Unnamed: 0.1', 
                'is_veg', 'Nutrition Density', 'level_0', 'rank', '_id']


def calculate_meal_totals(items):
    """
    Aggregate nutritional values from multiple food items.
    
    Args:
        items: List of food item dictionaries with nutritional data
        
    Returns:
        Dictionary with summed values for all numeric nutrients
    """
    if not items:
        return {}
    
    totals = {}
    
    for item in items:
        for key, value in item.items():
            if key in EXCLUDE_KEYS:
                continue
            try:
                val = float(value)
                totals[key] = totals.get(key, 0) + val
            except (ValueError, TypeError):
                pass
    
    return totals


def get_major_nutrients(item):
    """
    Extract major nutrients from a food item.
    
    Args:
        item: Food item dictionary
        
    Returns:
        Dictionary with major nutrient values
    """
    return {
        nutrient: item.get(nutrient, 0) 
        for nutrient in MAJOR_NUTRIENTS
    }


def get_detailed_nutrients(item, exclude_majors=True):
    """
    Get detailed nutrient breakdown, sorted by value.
    
    Args:
        item: Food item dictionary
        exclude_majors: Whether to exclude major nutrients from result
        
    Returns:
        List of (nutrient_name, value) tuples sorted by value descending
    """
    exclude = set(EXCLUDE_KEYS)
    if exclude_majors:
        exclude.update(MAJOR_NUTRIENTS)
    
    nutrients = []
    for key, value in item.items():
        if key in exclude:
            continue
        try:
            val = float(value)
            if val > 0:
                nutrients.append((key, val))
        except (ValueError, TypeError):
            pass
    
    # Sort by value descending
    return sorted(nutrients, key=lambda x: x[1], reverse=True)


def calculate_daily_value_percentage(nutrient, amount):
    """
    Calculate percentage of daily recommended value.
    Based on FDA daily values (2000 calorie diet).
    
    Args:
        nutrient: Name of nutrient
        amount: Amount in the food item
        
    Returns:
        Percentage of daily value (0-100+)
    """
    # Daily values based on FDA recommendations
    DAILY_VALUES = {
        'Caloric Value': 2000,
        'Fat': 78,           # grams
        'Saturated Fats': 20, # grams
        'Carbohydrates': 275, # grams
        'Sugars': 50,        # grams
        'Protein': 50,       # grams
        'Fiber': 28,         # grams
        'Sodium': 2300,      # mg
        'Cholesterol': 300,  # mg
        'Calcium': 1300,     # mg
        'Iron': 18,          # mg
        'Potassium': 4700,   # mg
        'Vitamin A': 900,    # mcg
        'Vitamin C': 90,     # mg
        'Vitamin D': 20,     # mcg
        'Vitamin E': 15,     # mg
        'Vitamin K': 120,    # mcg
        'Vitamin B1': 1.2,   # mg
        'Vitamin B2': 1.3,   # mg
        'Vitamin B3': 16,    # mg
        'Vitamin B6': 1.7,   # mg
        'Vitamin B12': 2.4,  # mcg
        'Zinc': 11,          # mg
        'Magnesium': 420,    # mg
    }
    
    if nutrient not in DAILY_VALUES or DAILY_VALUES[nutrient] == 0:
        return None
    
    return (amount / DAILY_VALUES[nutrient]) * 100


def classify_food_health_score(item):
    """
    Calculate a simple health score based on nutrient balance.
    
    Returns:
        Score from 0-100 and classification (Excellent/Good/Moderate/Poor)
    """
    score = 50  # Base score
    
    # Positive factors
    protein = float(item.get('Protein', 0))
    fiber = float(item.get('Fiber', 0))
    vitamins = sum(float(item.get(f'Vitamin {v}', 0)) for v in ['A', 'C', 'D', 'E', 'K'])
    
    score += min(protein * 2, 15)  # Up to 15 points for protein
    score += min(fiber * 3, 15)    # Up to 15 points for fiber
    score += min(vitamins * 0.5, 10)  # Up to 10 points for vitamins
    
    # Negative factors
    sugars = float(item.get('Sugars', 0))
    saturated = float(item.get('Saturated Fats', 0))
    sodium = float(item.get('Sodium', 0))
    
    score -= min(sugars * 0.5, 15)    # Up to -15 for high sugar
    score -= min(saturated * 1, 10)   # Up to -10 for saturated fat
    score -= min(sodium * 0.01, 10)   # Up to -10 for high sodium
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Classification
    if score >= 80:
        classification = "Excellent"
    elif score >= 60:
        classification = "Good"
    elif score >= 40:
        classification = "Moderate"
    else:
        classification = "Poor"
    
    return {"score": round(score), "classification": classification}
