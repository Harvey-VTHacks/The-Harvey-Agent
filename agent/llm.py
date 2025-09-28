import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Add parent directory to path for api_manager import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from api_manager import api_manager
except ImportError:
    api_manager = None
    print("⚠️ API Manager not found - using fallback single key")

def get_gemini_client():
    """Initialize and return a Gemini client with rotating API keys."""
    load_dotenv()
    
    try:
        # Try to get API key from manager first
        if api_manager:
            api_key = api_manager.get_available_key("flash")  # Use flash key for Harvey
            if api_key:
                print(f"🔑 Using Flash API key for Harvey agent")
                client = genai.Client(api_key=api_key)
                return client
        
        # Fallback to environment variables
        api_key = (os.getenv("GOOGLE_API_KEY_FLASH") or 
                  os.getenv("GEMINI_API_KEY") or 
                  os.getenv("GOOGLE_API_KEY"))
        
        if api_key:
            print(f"🔑 Using fallback API key for Harvey")
            client = genai.Client(api_key=api_key)
            return client
        else:
            raise ValueError("No API key found")
            
    except Exception as e:
        print(f"❌ Failed to configure Gemini client: {e}")
        # Last resort fallback
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return genai.Client(api_key=api_key)
        raise ValueError("GEMINI_API_KEY not found in environment variables")