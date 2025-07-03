import os
import sys
from other.settings_manager import settings_manager
from utils.path_utils import find_system_chromedriver, check_chrome_installation

def get_window_name():
    """Get the appropriate window name based on settings"""
    rename_window = settings_manager.get_setting("renameWindow", True)
    
    if rename_window:
        return "Notepad"
    else:
        return "InvisAI"

def get_window_icon():
    """Get the appropriate icon based on settings"""
    rename_window = settings_manager.get_setting("renameWindow", True)
    
    if rename_window:
        return "notepad.ico"
    else:
        return "google-eye.ico"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_chromedriver_path():
    """Get the path to chromedriver - checks bundled version first, then system installation"""
    # First, try to find ChromeDriver (bundled or system)
    system_chromedriver = find_system_chromedriver()
    if system_chromedriver:
        print(f"Found ChromeDriver at: {system_chromedriver}")
        return system_chromedriver
    
    # If ChromeDriver not found, check if Chrome is installed
    if not check_chrome_installation():
        print("Chrome is not installed. Please install Chrome first.")
        return None
    
    print("Chrome is installed but ChromeDriver not found.")
    print("Please download ChromeDriver from https://chromedriver.chromium.org/")
    print("Or install Chrome again to get the latest version with built-in ChromeDriver.")
    return None
