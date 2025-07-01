import webview
import pyautogui
import pynput.mouse as mouse
from mouse_handler import MouseHandler
from image_text import textFromImage
from ai import doAI

class ScreenCaptureAPI:
    def __init__(self):
        self.firstCorner = None
        self.secondCorner = None
        self.mouseListener = None
        self.isCapturing = False
        self.waitingForRelease = False
        self.mouseHandler = MouseHandler(self)
        
    def startCapture(self):
        self.firstCorner = None
        self.secondCorner = None
        self.isCapturing = True
        self.waitingForRelease = False
        
        try:
            self.mouseListener = mouse.Listener(
                on_click=self.mouseHandler.onMouseClick,
            )
            self.mouseListener.start()
            
            # Update button text to show first instruction
            webview.windows[0].evaluate_js('startBtn.textContent = "Click first corner..."')
            
            return {"success": True, "message": "Capture started. Left-click first corner."}
        except Exception as e:
            return {"success": False, "message": f"Failed to start capture: {str(e)}"}
    
    def cancelCapture(self):
        self.isCapturing = False
        self.stopMouseListener()
        self.firstCorner = None
        self.secondCorner = None
        self.waitingForRelease = False
        return {"success": True, "message": "Capture cancelled"}
    
    def stopMouseListener(self):
        if self.mouseListener:
            try:
                self.mouseListener.stop()
                self.mouseListener.join(timeout=1)
            except:
                pass
            finally:
                self.mouseListener = None
    
    def captureArea(self):
        if not (self.firstCorner and self.secondCorner):
            return {"success": False, "message": "Invalid coordinates"}
        
        try:
            x1, y1 = self.firstCorner
            x2, y2 = self.secondCorner
            
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
            
            # Convert screenshot to base64 data URL for display in browser
            import io
            import base64
            
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)
            
            image_data = base64.b64encode(buffer.getvalue()).decode()
            data_url = f"data:image/png;base64,{image_data}"
            
            self.isCapturing = False
            self.firstCorner = None
            self.secondCorner = None
            self.waitingForRelease = False
            
            # Pass the data URL to the JavaScript function
            webview.windows[0].evaluate_js(f'captureComplete("{data_url}")')
            
            doAI(data_url)  # Call AI processing function
            
            return {"success": True, "data_url": data_url}
            
        except Exception as e:
            webview.windows[0].evaluate_js(f'captureError("{str(e)}")')
            return {"success": False, "message": str(e)}
