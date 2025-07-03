import webview
from apis.screen_capture_api import ScreenCaptureAPI
from apis.window_api import WindowAPI
from other.settings_manager import settings_manager
from other.har_capture import get_har_capture_instance, cleanup_har_capture
import subprocess
import sys
from pynput import keyboard

class MainAPI:
    """
    Main API class that serves as the entry point for pywebview.
    This class delegates to specialized APIs for different functionalities.
    """
    
    def __init__(self):
        self.screen_capture = ScreenCaptureAPI()
        self.window = WindowAPI()
        self.keyboard_listener = None
        self.start_keyboard_listener()
    
    def start_keyboard_listener(self):
        """Start the keyboard listener for global hotkeys"""
        from pynput import mouse
        
        def on_key_press(key):
            try:
                if key == keyboard.Key.esc:
                    # Check if we're currently capturing
                    if hasattr(self.screen_capture, 'isCapturing') and self.screen_capture.isCapturing:
                        self.cancelCapture()
                        # Notify the frontend
                        try:
                            webview.windows[0].evaluate_js("captureError('Capture cancelled by user')")
                        except:
                            pass
                
                # Handle 's' key for starting capture
                elif hasattr(key, 'char') and key.char == 's':
                    # Check if S hotkey is enabled in settings
                    if settings_manager.get_setting("enableSHotkey", False):
                        # Only start capture if we're not already capturing
                        if not (hasattr(self.screen_capture, 'isCapturing') and self.screen_capture.isCapturing):
                            self.startCapture()
                            # Notify the frontend
                            try:
                                webview.windows[0].evaluate_js("onCaptureStart()")
                            except:
                                pass
                
                # Also restore window on any key press if it's transparent
                if hasattr(self.window, 'is_transparent') and self.window.is_transparent:
                    self.restore_window()
                    try:
                        webview.windows[0].evaluate_js("updatePreviewState(false)")
                    except:
                        pass
            except AttributeError:
                pass
        
        def on_key_release(key):
            pass
            
        def on_click(x, y, button, pressed):
            # Restore window on mouse click if it's minimized
            if pressed and hasattr(self.window, 'is_transparent') and self.window.is_transparent:
                self.restore_window()
                try:
                    webview.windows[0].evaluate_js("updatePreviewState(false)")
                except:
                    pass
                    
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=on_key_press,
            on_release=on_key_release
        )
        
        # Also start a mouse listener
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()
        self.keyboard_listener.start()
    
    def stop_keyboard_listener(self):
        """Stop the keyboard and mouse listeners"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            self.mouse_listener.stop()
    
    # Screen Capture API methods
    def startCapture(self):
        """Start screen capture process"""
        return self.screen_capture.startCapture()
    
    def cancelCapture(self):
        """Cancel ongoing screen capture"""
        return self.screen_capture.cancelCapture()
    
    def installTesseract(self):
        """Install Tesseract OCR"""
        return self.screen_capture.installTesseract()
    
    # Window API methods
    def startWindowDrag(self, startX, startY):
        """Start window dragging"""
        return self.window.startWindowDrag(startX, startY)
    
    def dragWindow(self, deltaX, deltaY):
        """Drag window by delta values"""
        return self.window.dragWindow(deltaX, deltaY)
    
    def endWindowDrag(self):
        """End window dragging"""
        return self.window.endWindowDrag()
    
    def closeWindow(self):
        """Close the application window"""
        return self.window.closeWindow()
        
    def set_window_transparent(self):
        """Make window transparent"""
        return self.window.set_window_transparent()
        
    def restore_window(self):
        """Restore window from transparent state"""
        return self.window.restore_window()

    # Settings API methods
    def getSettings(self):
        """Get all settings"""
        return settings_manager.get_all_settings()
    
    def updateSetting(self, key, value):
        """Update a specific setting"""
        success = settings_manager.update_setting(key, value)
        if success:
            print(f"Setting updated: {key} = {value}")
            # Apply setting changes immediately if needed
            if key == "renameWindow":
                self._apply_rename_setting(value)
            elif key.startswith("enable") and key.endswith(("Copilot", "Gemini")):
                # Handle AI enable/disable changes
                self._apply_ai_setting(key, value)
        return success
    
    def _apply_ai_setting(self, setting_key, enabled):
        """Apply AI enable/disable setting changes"""
        ai_name = setting_key.replace("enable", "").lower()
        
        if ai_name == "copilot":
            if not enabled:
                # Disable Copilot in UI
                try:
                    webview.windows[0].evaluate_js("document.querySelector('#copilot').classList.add('perma-disabled')")
                except:
                    pass
            else:
                # Re-enable Copilot if available
                from ai.ai_checks import checkCopilot
                if checkCopilot():
                    try:
                        webview.windows[0].evaluate_js("document.querySelector('#copilot').classList.remove('perma-disabled')")
                    except:
                        pass
        
        elif ai_name == "gemini":
            if not enabled:
                # Disable Gemini in UI
                try:
                    webview.windows[0].evaluate_js("document.querySelector('#gemini').classList.add('perma-disabled')")
                except:
                    pass
            else:
                # Re-enable Gemini if available
                from ai.ai_checks import checkGemini
                if checkGemini():
                    try:
                        webview.windows[0].evaluate_js("document.querySelector('#gemini').classList.remove('perma-disabled')")
                    except:
                        pass
        
        print(f"AI setting applied: {setting_key} = {enabled}")
    
    def _apply_rename_setting(self, enabled):
        """Apply the rename window setting immediately"""
        print(f"Rename window setting {'enabled' if enabled else 'disabled'}")
        print("Icon will be applied on next app startup")

    def restartApp(self):
        """Restart the application"""
        try:
            # Get the current executable path
            current_executable = sys.executable
            current_script = sys.argv[0]
            
            # Stop the keyboard listener before restarting
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            # Close the current webview first
            def close_and_restart():
                try:
                    # Start a new instance of the application
                    if getattr(sys, 'frozen', False):
                        # If running as a compiled executable
                        subprocess.Popen([current_executable] + sys.argv[1:])
                    else:
                        # If running as a Python script
                        subprocess.Popen([current_executable, current_script] + sys.argv[1:])
                    
                    # Force exit the current process
                    import os
                    os._exit(0)
                    
                except Exception as e:
                    print(f"Error in close_and_restart: {e}")
                    os._exit(1)
            
            # Use a timer to delay the restart slightly
            import threading
            restart_timer = threading.Timer(0.5, close_and_restart)
            restart_timer.start()
            
            return {"success": True, "message": "App restart initiated"}
            
        except Exception as e:
            print(f"Error restarting app: {e}")
            return {"success": False, "message": str(e)}

    # HAR Capture API methods
    def startHarCapture(self):
        """Start HAR capture for Copilot authentication"""
        try:
            har_capture = get_har_capture_instance()
            
            # Set up callback for when browser closes unexpectedly
            def on_browser_closed():
                try:
                    # Notify the frontend that browser was closed
                    webview.windows[0].evaluate_js("onHarCaptureBrowserClosed()")
                except:
                    pass
            
            har_capture.set_browser_closed_callback(on_browser_closed)
            success = har_capture.start_background_capture()
            
            if success:
                return {"success": True, "message": "HAR capture started"}
            else:
                return {"success": False, "message": "Failed to start HAR capture"}
                
        except Exception as e:
            print(f"Error starting HAR capture: {e}")
            return {"success": False, "message": str(e)}
    
    def completeHarCapture(self):
        """Complete HAR capture and save the file"""
        try:
            har_capture = get_har_capture_instance()
            success = har_capture.complete_capture()
            
            # Clean up the instance
            cleanup_har_capture()
            
            if success:
                return {"success": True, "message": "HAR capture completed and saved"}
            else:
                return {"success": False, "message": "Failed to complete HAR capture"}
                
        except Exception as e:
            print(f"Error completing HAR capture: {e}")
            return {"success": False, "message": str(e)}
    
    def getHarCaptureStatus(self):
        """Get the current status of HAR capture"""
        try:
            har_capture = get_har_capture_instance()
            return {
                "success": True,
                "active": har_capture.is_active(),
                "browser_open": har_capture.is_browser_open(),
                "completed": har_capture.completed
            }
        except Exception as e:
            print(f"Error getting HAR capture status: {e}")
            return {"success": False, "message": str(e)}

    def recheckAIAvailability(self):
        """Recheck AI availability and update UI accordingly"""
        try:
            from ai.ai_checks import checkCopilot, checkGemini
            
            # Check if Copilot is now available
            if checkCopilot():
                print("Copilot is now available")
                return {"success": True, "copilot_enabled": True}
            else:
                print("Copilot is still not available")
                return {"success": True, "copilot_enabled": False}
                
        except Exception as e:
            print(f"Error rechecking AI availability: {e}")
            return {"success": False, "message": str(e)}
