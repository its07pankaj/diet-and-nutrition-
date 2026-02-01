import pandas as pd
import json
import os

# Configuration
# Adjust paths to match your actual file system
BASE_DIR = r"e:\project\AI edit\antigravity\nutrition and deit\v2"
INPUT_CSV = os.path.join(BASE_DIR, "nutrition", "DeitNotify", "nutrition prediction", "dataset", "combined_food_data.csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "frontend", "assets", "data", "nutrition_db.json")

# Non-Vegetarian Keywords to Filter Out
NON_VEG_KEYWORDS = [
    "chicken", "beef", "pork", "ham", "turkey", "fish", "salmon", "tuna", 
    "shrimp", "crab", "lobster", "oyster", "clam", "mussel", "egg", 
    "sausage", "bacon", "pepperoni", "meat", "steak", "burger", 
    "lamb", "mutton", "veal", "duck", "goose", "anchovy", "sardine", 
    "cod", "trout", "herring", "scallop", "squid", "octopus", "caviar",
    "roe", "prawn", "salami", "pastrami", "liver", "kidney", "heart",
    "gelatin", "lard", "suet"
]

# Exceptions (Veg items that might contain keywords, e.g., "Eggplant" - though unlikely in this dataset context, safe to be careful)
# For this specific dataset, simple keyword matching is usually effective, but we add exceptions if needed.
VEG_EXCEPTIONS = ["eggplant", "vegetable burger", "veggie burger"]

def is_vegetarian(food_name):
    food_name = str(food_name).lower()
    
    # Check exceptions first
    for exc in VEG_EXCEPTIONS:
        if exc in food_name:
            return True
            
    # Check non-veg keywords
    for keyword in NON_VEG_KEYWORDS:
        # We ensure word boundaries or simple containment
        # Simple containment is stricter (safer for "strictly veg")
        if keyword in food_name:
            return False
    return True

def convert_data():
    print(f"Reading data from: {INPUT_CSV}")
    
    if not os.path.exists(INPUT_CSV):
        print("Error: Input file not found.")
        return

    try:
        df = pd.read_csv(INPUT_CSV)
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Replace NaN with 0 or empty string
        df = df.fillna(0)
        
        original_count = len(df)
        print(f"Original entries: {original_count}")
        
        # Filter for Vegetarian
        if 'food' in df.columns:
            df['is_veg'] = df['food'].apply(is_vegetarian)
            veg_df = df[df['is_veg'] == True]
            veg_df = veg_df.drop(columns=['is_veg'])
        else:
            print("Error: 'food' column not found.")
            return

        filtered_count = len(veg_df)
        print(f"Vegetarian filtered entries: {filtered_count}")
        print(f"Removed {original_count - filtered_count} non-vegetarian items.")

        # Convert to list of dictionaries
        data = veg_df.to_dict(orient='records')
        
        # Ensure output directory exists is handled by the mkdir command previously run, 
        # but os.makedirs is safe if it exists.
        os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
        
        with open(OUTPUT_JSON, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Success! JSON saved to: {OUTPUT_JSON}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    convert_data()
