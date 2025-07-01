import pynput.mouse as mouse
import webview
import threading


class MouseHandler:
    def __init__(self, captureApi):
        self.captureApi = captureApi
        
    def onMouseClick(self, x, y, button, pressed):
        if not self.captureApi.isCapturing:
            return
        
        if button == mouse.Button.left:
            if self.captureApi.firstCorner is None and pressed:
                self.captureApi.firstCorner = (int(x), int(y))
                webview.windows[0].evaluate_js('startBtn.textContent = "Click second corner..."')
                
            elif self.captureApi.firstCorner is not None and not self.captureApi.waitingForRelease and pressed:
                self.captureApi.secondCorner = (int(x), int(y))
                self.captureApi.waitingForRelease = True
                webview.windows[0].evaluate_js('startBtn.textContent = "Release to capture..."')
                
            elif self.captureApi.waitingForRelease and not pressed:
                webview.windows[0].evaluate_js('startBtn.textContent = "Capturing..."')
                self.captureApi.stopMouseListener()
                threading.Timer(0.1, self.captureApi.captureArea).start()
