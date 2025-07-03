print("Starting App...")

# Set environment to prevent console windows
import os
os.environ['PYTHONHIDEWINDOWS'] = '1'

# Prevent Selenium Manager from running to avoid Git window flash
os.environ['SE_DISABLE_SELENIUM_MANAGER'] = '1'
os.environ['SE_AVOID_STATS'] = '1'
os.environ['WDM_LOG_LEVEL'] = '0'  # Disable WebDriver Manager logging
if os.name == 'nt':  # Windows
    import sys
    if hasattr(sys, 'frozen'):
        # Hide console window for PyInstaller executable
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        SW_HIDE = 0
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, SW_HIDE)

# Patch subprocess to prevent window flashes BEFORE any other imports
import subprocess
if hasattr(subprocess, 'CREATE_NO_WINDOW'):
    subprocess._original_run = subprocess.run
    subprocess._original_Popen = subprocess.Popen
    
    def patched_run(*args, **kwargs):
        if 'creationflags' not in kwargs and hasattr(subprocess, 'CREATE_NO_WINDOW'):
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess._original_run(*args, **kwargs)
    
    class PatchedPopen(subprocess._original_Popen):
        def __init__(self, *args, **kwargs):
            if 'creationflags' not in kwargs and hasattr(subprocess, 'CREATE_NO_WINDOW'):
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            super().__init__(*args, **kwargs)
    
    subprocess.run = patched_run
    subprocess.Popen = PatchedPopen

import threading
import os
import time
from other.loading_screen import create_loading_window
root, _ = create_loading_window()

def start():
    print("Starting InvisAI...")

    htmlFile = resource_path("ui/index.html")
    print(f"HTML file path: {htmlFile}")
    print(f"HTML file exists: {os.path.exists(htmlFile)}")
    
    api = MainAPI()
    window_name = get_window_name()
    window_icon = get_window_icon()

    # Create webview window
    window = webview.create_window(
        window_name,
        htmlFile,
        js_api=api,
        width=300,
        height=400,
        on_top=True,
        shadow=True,
        frameless=True,
    )
    print(f"Running in thread: {threading.current_thread().name}")
    webview.start(
        lambda: windowCreated(window_name),
        debug=False,
        icon=resource_path(window_icon),
    )

def imports():
    global webview, MainAPI, windowCreated, get_window_name, get_window_icon, resource_path
    try:
        print('Starting imports...')

        # Initialize COM for this thread (needed for Windows-specific libraries)
        com_initialized = False
        try:
            import pythoncom
            pythoncom.CoInitialize()
            com_initialized = True
            print('COM initialized')
        except Exception as com_e:
            print(f'Warning: Could not initialize COM: {com_e}')
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import webview
        print('Webview imported')
        from apis.main_api import MainAPI
        print('MainAPI imported')
        from window_manager import windowCreated
        print('windowCreated imported')
        from utils.app_utils import get_window_name, get_window_icon, resource_path
        print('app_utils imported')
        print('Done importing!')

        # Clean up COM
        if com_initialized:
            try:
                pythoncom.CoUninitialize()
                print('COM cleaned up')
            except:
                pass

        return True
    except Exception as e:
        print(f'Import error: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    imports_done = threading.Event()
    imports_successful = threading.Event()

    def do_imports():
        success = imports()
        if success:
            imports_successful.set()
        imports_done.set()

    def check_imports_and_start():
        if imports_done.is_set():
            if imports_successful.is_set():
                print('Imports done successfully, running main...')
                root.destroy()
                start()
            else:
                print('Imports failed! Exiting...')
                root.destroy()
                import sys
                sys.exit(1)
        else:
            # Check again in 100ms
            root.after(100, check_imports_and_start)

    threading.Thread(target=do_imports, daemon=True).start()

    root.after(100, check_imports_and_start)

    root.mainloop()

if __name__ == '__main__':
    main()
