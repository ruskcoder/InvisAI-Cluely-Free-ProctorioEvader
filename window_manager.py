import ctypes
from ctypes import wintypes
import time
import win32gui
import webview
from ai_checks import checkGemini
from image_text import checkTesseract

WDA_EXCLUDEFROMCAPTURE = 0x00000011
# Define constants for no-activate functionality
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
GWL_EXSTYLE = -20


def apply_noactivate(hwnd):
    ex_style = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)
    ex_style |= WS_EX_NOACTIVATE
    time.sleep(1) 
    print(f"Applying no-activate style to window: {hwnd}")
    win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, ex_style)

def afterWindowVisible():
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    setWindowDisplayAffinity = user32.SetWindowDisplayAffinity
    setWindowDisplayAffinity.argtypes = wintypes.HWND, wintypes.DWORD
    setWindowDisplayAffinity.restype = wintypes.BOOL

    windowHandle = win32gui.FindWindow(None, "InvisAI")
    if not windowHandle:
        webview.windows[0].evaluate_js("showError()")
        print("Could not find window")
    # getForegroundWindow = user32.GetForegroundWindow
    # getForegroundWindow.argtypes = ()
    # getForegroundWindow.restype = wintypes.HWND

    # windowHandle = getForegroundWindow()
    result = setWindowDisplayAffinity(windowHandle, WDA_EXCLUDEFROMCAPTURE)
    if result:
        print("Window is now hidden from screen capture.")
    else:
        webview.windows[0].evaluate_js("showError()")
        print(f"Failed to set display affinity. Error code: {ctypes.get_last_error()}")
    return windowHandle

def windowCreated():
    try:
        time.sleep(0.2)
        windowHandle = afterWindowVisible()
        apply_noactivate(windowHandle)
    
    except Exception as e:
        print(f"Failed to protect window: {e}")
        webview.windows[0].evaluate_js("showError()")
    
    if not checkGemini():
        webview.windows[0].evaluate_js("disableGemini()")
        print("Gemini is not available. Disabling Gemini feature in UI.")

    if not checkTesseract():
        webview.windows[0].evaluate_js("warningTesseract()")
        print("Tesseract is not installed. Disabling some features in UI.")