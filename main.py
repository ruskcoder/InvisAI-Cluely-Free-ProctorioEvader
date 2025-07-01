import webview
import os
import sys
from main_api import MainAPI
from window_manager import windowCreated


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def createApp():
    htmlFile = resource_path(os.path.join('ui', 'index.html'))
    api = MainAPI()
    window = webview.create_window(
        'InvisAI',
        htmlFile,
        js_api=api,
        width=300,
        height=400,
        # min_size=(350, 500),
        on_top=True,
        shadow=True,
        frameless=True,
    )
    webview.start(windowCreated, debug=False, icon=resource_path('eye.png'))


if __name__ == '__main__':
    print("Starting application...")
    createApp()
