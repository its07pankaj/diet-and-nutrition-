"""
Test script to verify Gemini AI API connection and response
"""
import json

# Test both API keys
API_KEYS = [
    "AIzaSyBxsSLs-so8Y6h6MwzI1w9ftZfPxyEoINI",
    "AIzaSyA5tO8SEAL0QTohDzldYhtIsQGZXx3FpmY"
]

def test_api_key(api_key):
    print(f"\n{'='*50}")
    print(f"Testing API Key: {api_key[:20]}...")
    print('='*50)
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        print("[OK] Client initialized successfully")
        
        # Simple test prompt
        test_prompt = """You are a nutrition expert. 
        Return a simple JSON with these exact fields:
        {"status": "success", "message": "API is working!", "model": "gemini-2.5-flash"}
        """
        
        print("[...] Making test API call...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=test_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=500
            )
        )
        
        print(f"[OK] Response received! Length: {len(response.text)} chars")
        print(f"\n--- Response ---\n{response.text}\n----------------")
        
        # Try to parse as JSON
        try:
            data = json.loads(response.text)
            print(f"[OK] Valid JSON response!")
            return True, data
        except json.JSONDecodeError as e:
            print(f"[WARN] Response is not valid JSON: {e}")
            return True, response.text
            
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("[FIX] Run: pip install google-genai")
        return False, str(e)
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   GEMINI API TEST SCRIPT FOR DIETNOTIFY")
    print("=" * 60)
    
    for i, key in enumerate(API_KEYS):
        success, result = test_api_key(key)
        if success:
            print(f"\n✅ API Key #{i+1} WORKS!")
            break
        else:
            print(f"\n❌ API Key #{i+1} FAILED")
    
    print("\n" + "=" * 60)
    print("   TEST COMPLETE")
    print("=" * 60)
