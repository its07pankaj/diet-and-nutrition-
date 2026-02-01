import pandas as pd
import glob
import os

class DataLoader:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data = pd.DataFrame()
        self.non_veg_keywords = [
            "chicken", "beef", "pork", "ham", "turkey", "fish", "salmon", "tuna", 
            "shrimp", "crab", "lobster", "oyster", "clam", "mussel", "egg", 
            "sausage", "bacon", "pepperoni", "meat", "steak", "burger", 
            "lamb", "mutton", "veal", "duck", "goose", "squid", "octopus", 
            "liver", "kidney", "heart", "gelatin"
        ]
        # Exceptions (Veg items that might contain keywords)
        self.veg_exceptions = ["eggplant", "vegetable burger", "veggie burger"]

    def load_all_data(self):
        print("Initializing Data Pipeline...")
        all_dfs = []

        # 1. Load Combined Data (Primary)
        combined_path = os.path.join(self.base_dir, "data", "nutrition_db", "DeitNotify", "nutrition prediction", "dataset", "combined_food_data.csv")
        print(f"Checking path: {combined_path}")
        print(f"Path exists: {os.path.exists(combined_path)}")
        if os.path.exists(combined_path):
            try:
                print(f"Loading Primary Dataset: {combined_path}")
                df1 = pd.read_csv(combined_path, encoding='utf-8')
                df1.columns = df1.columns.str.strip()
                all_dfs.append(df1)
                print(f"Loaded {len(df1)} records from combined_food_data.csv")
            except Exception as e:
                print(f"Error loading {combined_path}: {e}")
        else:
            print(f"WARNING: Combined data file not found at {combined_path}")

        # 2. Load Group Data (Supplemental)
        # Pattern: data/nutrition_db/FINAL FOOD DATASET/FOOD-DATA-GROUP*.csv
        group_path_pattern = os.path.join(self.base_dir, "data", "nutrition_db", "FINAL FOOD DATASET", "FOOD-DATA-GROUP*.csv")
        group_files = glob.glob(group_path_pattern)
        
        for f in group_files:
            try:
                print(f"Loading Group Dataset: {f}")
                df_g = pd.read_csv(f, encoding='utf-8')
                df_g.columns = df_g.columns.str.strip()
                all_dfs.append(df_g)
                print(f"Loaded {len(df_g)} records from {os.path.basename(f)}")
            except Exception as e:
                print(f"Error loading {f}: {e}")

        # 3. Load Indian Foods Dataset (NEW)
        indian_foods_path = os.path.join(self.base_dir, "data", "nutrition_db", "indian_foods.csv")
        if os.path.exists(indian_foods_path):
            try:
                print(f"Loading Indian Foods Dataset: {indian_foods_path}")
                df_indian = pd.read_csv(indian_foods_path, encoding='utf-8')
                df_indian.columns = df_indian.columns.str.strip()
                all_dfs.append(df_indian)
                print(f"Loaded {len(df_indian)} records from indian_foods.csv")
            except Exception as e:
                print(f"Error loading Indian foods: {e}")

        if not all_dfs:
            print("CRITICAL: No data loaded.")
            return

        # 3. Merge
        # We use concat. Columns that don't match will be filled with NaN (later 0)
        self.data = pd.concat(all_dfs, ignore_index=True)
        print(f"Total Raw Records: {len(self.data)}")

        # 4. Filter Duplicates (by Food Name)
        if 'food' in self.data.columns:
            self.data.drop_duplicates(subset=['food'], keep='first', inplace=True)
        
        # 5. Vegetarian Filter
        self._apply_veg_filter()
        
        # 6. Clean Nans
        self.data.fillna(0, inplace=True)
        
        print(f"Final Knowledge Base Size: {len(self.data)} items.")

    def _apply_veg_filter(self):
        if 'food' not in self.data.columns:
            return

        def is_veg(name):
            name = str(name).lower()
            for exc in self.veg_exceptions:
                if exc in name: return True
            for kw in self.non_veg_keywords:
                if kw in name: return False
            return True

        self.data = self.data[self.data['food'].apply(is_veg)]

    def search(self, query, limit=20):
        if self.data.empty: return []
        
        query = query.lower()
        # Simple text search (can be upgraded to TF-IDF)
        matches = self.data[self.data['food'].str.lower().str.contains(query, na=False)]
        
        # Sort: Exact start first
        matches['rank'] = matches['food'].apply(lambda x: 0 if x.lower().startswith(query) else 1)
        matches = matches.sort_values('rank')
        
        return matches.head(limit).to_dict(orient='records')

    def get_dataframe(self):
        return self.data
