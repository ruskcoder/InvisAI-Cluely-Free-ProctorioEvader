import os
from datetime import datetime


def generateFilename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"screenshot_{timestamp}.png"


def getScreenshotsList():
    try:
        files = [f for f in os.listdir('.') if f.startswith('screenshot_') and f.endswith('.png')]
        files.sort(reverse=True)
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "message": str(e)}


def deleteScreenshot(filename):
    try:
        if os.path.exists(filename) and filename.startswith('screenshot_'):
            os.remove(filename)
            return {"success": True, "message": f"Deleted {filename}"}
        else:
            return {"success": False, "message": "File not found or invalid filename"}
    except Exception as e:
        return {"success": False, "message": str(e)}
