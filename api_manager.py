#!/usr/bin/env python3
"""
API Key Manager for Harvey Project
Manages 5 different API keys to distribute load and avoid rate limiting
"""

import os
import random
import time
from pathlib import Path

class APIKeyManager:
    def __init__(self):
        self.load_api_keys()
        self.usage_tracker = {}
        self.current_key_index = 0
        
    def load_api_keys(self):
        """Load all 5 API keys from .env"""
        # Load from environment variables
        self.api_keys = {
            'voice': os.getenv("GOOGLE_API_KEY_VOICE"),
            'flash': os.getenv("GOOGLE_API_KEY_FLASH"), 
            'completion1': os.getenv("GOOGLE_API_KEY_1"),
            'completion2': os.getenv("GOOGLE_API_KEY_2"),
            'completion3': os.getenv("GOOGLE_API_KEY_3")
        }
        
        # Filter out None values
        self.api_keys = {k: v for k, v in self.api_keys.items() if v}
        
        if not self.api_keys:
            print("❌ No API keys found! Please set up your .env file:")
            print("GOOGLE_API_KEY_VOICE=your_voice_key")
            print("GOOGLE_API_KEY_FLASH=your_flash_key") 
            print("GOOGLE_API_KEY_1=your_completion_key_1")
            print("GOOGLE_API_KEY_2=your_completion_key_2")
            print("GOOGLE_API_KEY_3=your_completion_key_3")
            return
            
        print(f"✅ Loaded {len(self.api_keys)} API keys: {list(self.api_keys.keys())}")
        
    def get_key_for_service(self, service_type):
        """Get appropriate API key for service type"""
        
        if service_type == "voice" and "voice" in self.api_keys:
            return self.api_keys["voice"]
            
        elif service_type == "flash" and "flash" in self.api_keys:
            return self.api_keys["flash"]
            
        elif service_type == "completion":
            # Rotate through completion keys
            completion_keys = [k for k in self.api_keys.keys() if k.startswith('completion')]
            if completion_keys:
                # Simple rotation
                key_name = completion_keys[self.current_key_index % len(completion_keys)]
                self.current_key_index += 1
                return self.api_keys[key_name]
                
        # Fallback: use any available key
        if self.api_keys:
            return list(self.api_keys.values())[0]
            
        return None
        
    def get_random_key(self):
        """Get a random key to distribute load"""
        if self.api_keys:
            return random.choice(list(self.api_keys.values()))
        return None
        
    def mark_rate_limited(self, api_key, retry_after=60):
        """Mark a key as rate limited"""
        self.usage_tracker[api_key] = {
            'rate_limited': True,
            'retry_after': time.time() + retry_after
        }
        print(f"⏳ API key marked as rate limited for {retry_after}s")
        
    def is_key_available(self, api_key):
        """Check if key is available (not rate limited)"""
        if api_key not in self.usage_tracker:
            return True
            
        tracker = self.usage_tracker[api_key]
        if tracker.get('rate_limited') and time.time() < tracker.get('retry_after', 0):
            return False
            
        return True
        
    def get_available_key(self, service_type="completion"):
        """Get an available (non-rate-limited) key"""
        preferred_key = self.get_key_for_service(service_type)
        
        if preferred_key and self.is_key_available(preferred_key):
            return preferred_key
            
        # Try all keys if preferred is rate limited
        for key in self.api_keys.values():
            if self.is_key_available(key):
                return key
                
        print("❌ All API keys are rate limited!")
        return None

# Global instance
api_manager = APIKeyManager()