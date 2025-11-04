"""
Quick script to check if the backend API is running
Requires: pip install requests
"""
import requests
import sys

def check_backend(url="http://localhost:8000"):
    """Check if backend is accessible"""
    try:
        print(f"Checking backend at {url}...")
        response = requests.get(f"{url}/health", timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Gemini configured: {data.get('gemini_configured', False)}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running!")
        print("\nTo start the backend:")
        print("1. Open a terminal/command prompt")
        print("2. Navigate to the backend folder:")
        print("   cd backend")
        print("3. Start the server:")
        print("   uvicorn main:app --reload")
        print("\nOr use the start script:")
        print("   start_backend.bat")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = check_backend(url)
    sys.exit(0 if success else 1)

