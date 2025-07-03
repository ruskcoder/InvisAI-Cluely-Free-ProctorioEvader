import json
import os
from utils.path_utils import get_app_directory

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.join(get_app_directory(), "settings.json")
        self.default_settings = {
            "renameWindow": True,  # Default to True to appear as Notepad
            "enableChatGPT": True,
            "enableCopilot": True,
            "enableGemini": True,
            "enableQwen": True,
            "enableDeepseek": True,
            "enableSHotkey": False  # Disable 'S' hotkey by default
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file, create with defaults if not exists"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = {**self.default_settings, **loaded_settings}
                return settings
            else:
                # Create settings file with defaults
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Save settings to JSON file"""
        try:
            settings_to_save = settings or self.settings
            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
            self.settings = settings_to_save
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def update_setting(self, key, value):
        """Update a specific setting and save to file"""
        self.settings[key] = value
        return self.save_settings()
    
    def get_all_settings(self):
        """Get all settings"""
        return self.settings.copy()

settings_manager = SettingsManager()
