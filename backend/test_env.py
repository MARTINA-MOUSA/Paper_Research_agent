"""
Test script to verify .env file is being read correctly
"""
import os
from pathlib import Path

# Check if .env exists
env_path = Path(".env")
if not env_path.exists():
    print(" .env file not found in current directory!")
    print(f"Current directory: {os.getcwd()}")
    print("\nPlease create .env file with:")
    print("  GEMINI_API_KEY=your_api_key_here")
    exit(1)

print(" .env file found")
print(f"Location: {env_path.absolute()}")
print()

# Try loading with dotenv
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    print(f" GEMINI_API_KEY found in environment")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
else:
    print(" GEMINI_API_KEY not found in .env file!")
    print("\nPlease add to .env:")
    print("  GEMINI_API_KEY=your_api_key_here")

print()

# Try loading with Pydantic Settings
try:
    from config import settings
    print(" Settings loaded from config.py")
    
    if settings.GEMINI_API_KEY:
        print(f" GEMINI_API_KEY found in settings")
        print(f"   Length: {len(settings.GEMINI_API_KEY)} characters")
        print(f"   Starts with: {settings.GEMINI_API_KEY[:10]}...")
    else:
        print(" GEMINI_API_KEY is empty in settings!")
        print("\nMake sure .env file has:")
        print("  GEMINI_API_KEY=your_actual_api_key")
except Exception as e:
    print(f" Error loading settings: {e}")
    import traceback
    traceback.print_exc()

