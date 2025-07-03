import ctypes
from ctypes import wintypes
import time
import os
import win32gui
import win32con
import webview
from ai.ai_checks import checkGemini, checkCopilot
from utils.image_text import checkTesseract
from other.settings_manager import settings_manager
from utils.app_utils import get_window_icon, resource_path

# Define constants for window styles
WDA_EXCLUDEFROMCAPTURE = 0x00000011
# Define constants for no-activate functionality
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
GWL_EXSTYLE = -20

# Icon-related constants
ICON_SMALL = 0
ICON_BIG = 1
WM_SETICON = 0x0080


def set_window_icon(hwnd, icon_path):
    """Set the window icon using Windows API"""
    try:
        # Get the full path to the icon
        full_icon_path = resource_path(icon_path)
        print(f"Setting window icon to: {full_icon_path}")
        
        if not os.path.exists(full_icon_path):
            print(f"Icon file not found: {full_icon_path}")
            return False
        
        # Load the icon from file
        # For PNG files, we'll use LoadImage with LR_LOADFROMFILE
        hicon = win32gui.LoadImage(
            0,  # hInstance
            full_icon_path,
            win32con.IMAGE_ICON,
            32, 32,  # Width, Height  
            win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        )
        
        # If that fails, try loading as bitmap and converting
        if not hicon:
            try:
                hicon = win32gui.LoadImage(
                    0,  # hInstance
                    full_icon_path,
                    win32con.IMAGE_BITMAP,
                    32, 32,  # Width, Height
                    win32con.LR_LOADFROMFILE
                )
            except:
                pass
        
        if hicon:
            # Set both small and large icons
            win32gui.SendMessage(hwnd, WM_SETICON, ICON_SMALL, hicon)
            win32gui.SendMessage(hwnd, WM_SETICON, ICON_BIG, hicon)
            
            # Force a repaint to update the icon
            win32gui.RedrawWindow(hwnd, None, None, win32con.RDW_FRAME | win32con.RDW_INVALIDATE)
            
            print(f"Successfully set window icon to {icon_path}")
            return True
        else:
            print(f"Failed to load icon from {icon_path}")
            return False
            
    except Exception as e:
        print(f"Error setting window icon: {e}")
        return False


def apply_noactivate(hwnd):
    ex_style = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)
    ex_style |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
    print(f"Applying no-activate and toolwindow styles to window: {hwnd}")
    win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, ex_style)
    win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                        win32con.SWP_NOMOVE | 
                        win32con.SWP_NOSIZE | 
                        win32con.SWP_NOZORDER | 
                        win32con.SWP_FRAMECHANGED)


def setAffinity(windowHandle):
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    setWindowDisplayAffinity = user32.SetWindowDisplayAffinity
    setWindowDisplayAffinity.argtypes = wintypes.HWND, wintypes.DWORD
    setWindowDisplayAffinity.restype = wintypes.BOOL

    result = setWindowDisplayAffinity(windowHandle, WDA_EXCLUDEFROMCAPTURE)
    if result:
        print("Window is now hidden from screen capture.")
    else:
        webview.windows[0].evaluate_js("showError()")
        print(f"Failed to set display affinity. Error code: {ctypes.get_last_error()}")


def windowCreated(window_name):
    time.sleep(0.2)
    if settings_manager.get_setting("enableGemini", True) and not checkGemini():
        webview.windows[0].evaluate_js("disableGemini()")
        print("Gemini is not available. Disabling Gemini feature in UI.")

    if settings_manager.get_setting("enableCopilot", True) and not checkCopilot():
        webview.windows[0].evaluate_js("disableCopilot()")
        print("Copilot HAR file is not available. Disabling Copilot feature in UI.")

    if not checkTesseract():
        webview.windows[0].evaluate_js("warningTesseract()")
        print("Tesseract is not installed. Disabling some features in UI.")

    attempts = 0
    windowHandle = None
    while attempts < 3 and not windowHandle:
        windowHandle = win32gui.FindWindow(None, window_name)
        if not windowHandle:
            print(f"Waiting for window handle... Attempt {attempts+1}")
            time.sleep(0.3)
        attempts += 1

    if not windowHandle:
        webview.windows[0].evaluate_js("showError()")
        print("Could not find window")
        return

    try:
        apply_noactivate(windowHandle)
        setAffinity(windowHandle)
        
        # Set the window icon based on current settings
        icon_path = get_window_icon()
        set_window_icon(windowHandle, icon_path)

    except Exception as e:
        print(f"Failed to protect window: {e}")
        webview.windows[0].evaluate_js("showError()")
