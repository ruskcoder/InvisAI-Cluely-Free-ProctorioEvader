import os
import sys
import subprocess

# Prevent Selenium Manager from running to avoid Git window flash
os.environ['SE_DISABLE_SELENIUM_MANAGER'] = '1'
os.environ['SE_AVOID_STATS'] = '1'

# Set global subprocess creation flags to prevent window flashes
if hasattr(subprocess, 'CREATE_NO_WINDOW'):
    subprocess._original_run = subprocess.run
    subprocess._original_Popen = subprocess.Popen
    
    def patched_run(*args, **kwargs):
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess._original_run(*args, **kwargs)
    
    class PatchedPopen(subprocess._original_Popen):
        def __init__(self, *args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            super().__init__(*args, **kwargs)
    
    subprocess.run = patched_run
    subprocess.Popen = PatchedPopen

def get_app_directory():
    """
    Get the directory where the application should store/read files.
    When running as a PyInstaller exe, this returns the directory containing the exe.
    When running as a script, this returns the project root directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe - return directory containing the exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script - return project root directory
        # Go up one level from utils directory to get project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_resource_path(relative_path):
    """
    Get the absolute path to a resource file.
    For PyInstaller, this looks in the temporary extraction directory.
    For script execution, this looks relative to the script.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe - use the temporary extraction directory
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    """
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

def find_system_chromedriver():
    """
    Find ChromeDriver on the system. Returns the path if found, None otherwise.
    First checks for bundled ChromeDriver, then falls back to system installation.
    """
    import subprocess
    import shutil
    
    # Debug PyInstaller environment if running as exe
    if getattr(sys, 'frozen', False):
        debug_pyinstaller_environment()
    
    # First, check for bundled ChromeDriver in the application directory
    bundled_chromedriver = get_resource_path("chromedriver.exe")
    print(f"Checking for bundled ChromeDriver at: {bundled_chromedriver}")
    if os.path.exists(bundled_chromedriver):
        print(f"Found bundled ChromeDriver: {bundled_chromedriver}")
        return bundled_chromedriver
    else:
        print("Bundled ChromeDriver not found, checking system PATH...")
    
    # Second, try to find chromedriver in PATH
    chromedriver_path = shutil.which("chromedriver")
    if chromedriver_path and os.path.exists(chromedriver_path):
        print(f"Found ChromeDriver in PATH: {chromedriver_path}")
        return chromedriver_path
    
    # Try common Chrome installation paths on Windows
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chromedriver.exe"),
    ]
    
    print("Checking common Chrome installation paths...")
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"Found ChromeDriver at: {path}")
            return path
    
    # Skip Chrome version check to avoid Git window flash
    # try:
    #     chrome_version = get_chrome_version()
    #     if chrome_version:
    #         print(f"Found Chrome version: {chrome_version}")
    #         # Could implement automatic download here, but for now just return None
    #         return None
    # except:
    #     pass
    
    print("ChromeDriver not found anywhere!")
    return None

def get_chrome_version():
    """
    Get the installed Chrome version on Windows.
    """
    import subprocess
    import re
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                # Use wmic instead of PowerShell to avoid Git window flash
                result = subprocess.run([
                    'wmic', 'datafile', 'where', f'name="{chrome_path.replace(chr(92), chr(92)+chr(92))}"', 
                    'get', 'Version', '/value'
                ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse wmic output
                    for line in result.stdout.split('\n'):
                        if 'Version=' in line:
                            version = line.split('Version=')[1].strip()
                            if version:
                                # Extract major version number
                                major_version = version.split('.')[0]
                                return major_version
            except:
                # Fallback to reading version from registry
                try:
                    import winreg
                    reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        version, _ = winreg.QueryValueEx(key, "version")
                        if version:
                            major_version = version.split('.')[0]
                            return major_version
                except:
                    continue
    
    return None

def check_chrome_installation():
    """
    Check if Chrome is installed on the system.
    Returns True if found, False otherwise.
    """
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            return True
    
    return False

def debug_pyinstaller_environment():
    """
    Debug function to print PyInstaller environment information.
    """
    print("=== PyInstaller Environment Debug ===")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    
    if hasattr(sys, '_MEIPASS'):
        print(f"sys._MEIPASS: {sys._MEIPASS}")
        print(f"Contents of _MEIPASS:")
        try:
            for item in os.listdir(sys._MEIPASS):
                item_path = os.path.join(sys._MEIPASS, item)
                if os.path.isfile(item_path):
                    print(f"  FILE: {item}")
                else:
                    print(f"  DIR:  {item}")
        except Exception as e:
            print(f"  Error listing _MEIPASS: {e}")
    else:
        print("sys._MEIPASS: Not available (not running from PyInstaller)")
    
    print(f"get_app_directory(): {get_app_directory()}")
    print(f"get_resource_path('chromedriver.exe'): {get_resource_path('chromedriver.exe')}")
    print("=====================================")
