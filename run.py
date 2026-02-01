from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🥗 DietNotify Professional Server (v2 Refactored)")
    print("=" * 50)
    print("🚀 App Structure: MVC Pattern")
    print("📂 Data Source:   data/nutrition_db")
    print("🌐 Dashboard:     http://localhost:5000")
    print("=" * 50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
