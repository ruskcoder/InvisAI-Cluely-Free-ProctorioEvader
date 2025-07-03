import pynput.mouse as mouse
import webview
import threading

class MouseEventsAPI:
    def __init__(self, screen_capture_api):
        self.screen_capture_api = screen_capture_api
        
    def onMouseClick(self, x, y, button, pressed):
        if not self.screen_capture_api.isCapturing:
            return
        
        if button == mouse.Button.left:
            if self.screen_capture_api.firstCorner is None and pressed:
                self.screen_capture_api.firstCorner = (int(x), int(y))
                webview.windows[0].evaluate_js('startBtn.textContent = "Click second corner..."')
                
            elif self.screen_capture_api.firstCorner is not None and not self.screen_capture_api.waitingForRelease and pressed:
                self.screen_capture_api.secondCorner = (int(x), int(y))
                self.screen_capture_api.waitingForRelease = True
                webview.windows[0].evaluate_js('startBtn.textContent = "Release to capture..."')
                
            elif self.screen_capture_api.waitingForRelease and not pressed:
                webview.windows[0].evaluate_js('startBtn.textContent = "Capturing..."')
                self.screen_capture_api.stopMouseListener()
                threading.Timer(0.1, self.screen_capture_api.captureArea).start()
