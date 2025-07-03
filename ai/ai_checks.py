from g4f.cookies import load_cookies_from_browsers
import os
from utils.path_utils import get_resource_path

enableGemini = True
enableQwen = True
enableDeepseek = True
enableCopilot = True

def disableTextModels():
    global enableQwen, enableDeepseek
    enableQwen = False
    enableDeepseek = False

def checkGemini():
    global enableGemini
    cook = load_cookies_from_browsers(".google.com")
    if "__Secure-1PSID" not in cook.keys():
        enableGemini = False
        return False
    return True

def checkCopilot():
    global enableCopilot
    # Check for HAR file in current working directory
    har_file_path = os.path.join(os.getcwd(), "har_and_cookies", "copilot.microsoft.com.har")
    if not os.path.exists(har_file_path):
        enableCopilot = False
        print("Copilot HAR file not found")
        return False
    try:
        with open(har_file_path, "r", encoding="utf-8") as f:
            har_content = f.read()
            if '"name": "authorization"' not in har_content:
                enableCopilot = False
                print("Authorization token not found in Copilot HAR file")
                return False
    except UnicodeDecodeError:
        # If UTF-8 fails, try with error handling
        try:
            with open(har_file_path, "r", encoding="utf-8", errors="ignore") as f:
                har_content = f.read()
                if '"name": "authorization"' not in har_content:
                    enableCopilot = False
                    print("Authorization token not found in Copilot HAR file")
                    return False
        except Exception as e:
            enableCopilot = False
            print(f"Error reading Copilot HAR file: {e}")
            return False
    except Exception as e:
        enableCopilot = False
        print(f"Error reading Copilot HAR file: {e}")
        return False
    enableCopilot = True
    return True