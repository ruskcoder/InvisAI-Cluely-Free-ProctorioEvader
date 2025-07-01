import webview

class WindowAPI:
    """
    API for handling window operations like dragging, minimizing, and closing.
    """
    
    def __init__(self):
        # Window dragging state
        self.drag_start_window_x = None
        self.drag_start_window_y = None
        self.drag_start_mouse_x = None
        self.drag_start_mouse_y = None
    
    def startWindowDrag(self, startX, startY):
        """Initialize window dragging with starting coordinates"""
        try:
            window = webview.windows[0]
            self.drag_start_window_x = window.x
            self.drag_start_window_y = window.y
            self.drag_start_mouse_x = startX
            self.drag_start_mouse_y = startY
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Failed to start drag: {str(e)}"}
    
    def dragWindow(self, deltaX, deltaY):
        """Move the window based on mouse movement delta"""
        try:
            window = webview.windows[0]
            new_x = self.drag_start_window_x + deltaX
            new_y = self.drag_start_window_y + deltaY
            window.move(new_x, new_y)
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Failed to drag window: {str(e)}"}
    
    def endWindowDrag(self):
        """End window dragging"""
        try:
            # Clean up drag state
            self.drag_start_window_x = None
            self.drag_start_window_y = None
            self.drag_start_mouse_x = None
            self.drag_start_mouse_y = None
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Failed to end drag: {str(e)}"}
    
    def closeWindow(self):
        """Close the application window"""
        try:
            window = webview.windows[0]
            window.destroy()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Failed to close window: {str(e)}"}
