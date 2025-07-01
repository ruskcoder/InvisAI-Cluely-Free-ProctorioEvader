import webview
from screen_capture_api import ScreenCaptureAPI
from window_api import WindowAPI

class MainAPI:
    """
    Main API class that serves as the entry point for pywebview.
    This class delegates to specialized APIs for different functionalities.
    """
    
    def __init__(self):
        self.screen_capture = ScreenCaptureAPI()
        self.window = WindowAPI()
        # Mouse events are handled internally by the screen capture API
    
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
