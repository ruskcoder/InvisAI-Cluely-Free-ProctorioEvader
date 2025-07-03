import webview
import ctypes
import win32gui
import win32con

class WindowAPI:
    """
    API for handling window operations like dragging, minimizing, and closing.
    """

    def __init__(self):
        self.drag_start_window_x = None
        self.drag_start_window_y = None
        self.drag_start_mouse_x = None
        self.drag_start_mouse_y = None
        self.scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.is_transparent = False
        self.original_window_pos = None

    def startWindowDrag(self, startX, startY):
        """Initialize window dragging with starting coordinates"""
        try:
            window = webview.windows[0]
            # Store initial window position
            self.drag_start_window_x = window.x
            self.drag_start_window_y = window.y
            # Store initial mouse position
            self.drag_start_mouse_x = startX
            self.drag_start_mouse_y = startY
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Failed to start drag: {str(e)}"}

    def dragWindow(self, currentX, currentY):
        """Move the window based on current mouse position"""
        try:
            if (self.drag_start_window_x is None or self.drag_start_window_y is None or 
                self.drag_start_mouse_x is None or self.drag_start_mouse_y is None):
                return {"success": False, "message": "Drag not initialized"}

            window = webview.windows[0]

            deltaX = currentX - self.drag_start_mouse_x
            deltaY = currentY - self.drag_start_mouse_y

            new_x = self.drag_start_window_x + deltaX
            new_y = self.drag_start_window_y + deltaY

            if new_x < -100:
                new_x = -100
            if new_y < 0:
                new_y = 0
            new_x = int(new_x / self.scaleFactor)
            new_y = int(new_y / self.scaleFactor)
            
            window.move(int(new_x), int(new_y))
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Failed to drag window: {str(e)}"}

    def endWindowDrag(self):
        """End window dragging"""
        try:
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
            
    def set_window_transparent(self):
        """Make window fully transparent (invisible) but keep it in place"""
        try:
            if self.is_transparent:
                return {"success": True, "message": "Window is already transparent"}
                
            window = webview.windows[0]
            hwnd = win32gui.FindWindow(None, window.title)
            
            if not hwnd:
                return {"success": False, "message": "Could not find window"}
                
            # Save current window position
            rect = win32gui.GetWindowRect(hwnd)
            self.original_window_pos = rect
            
            # Get window's extended style
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # Add layered window style (needed for transparency)
            win32gui.SetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE,
                ex_style | win32con.WS_EX_LAYERED
            )
            
            # Make fully transparent (alpha = 0)
            ctypes.windll.user32.SetLayeredWindowAttributes(
                hwnd, 0, 0, win32con.LWA_ALPHA
            )
            
            # Also make the window click-through so it doesn't interfere with clicking
            new_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(
                hwnd, 
                win32con.GWL_EXSTYLE,
                new_ex_style | win32con.WS_EX_TRANSPARENT
            )
            
            self.is_transparent = True
            
            return {"success": True, "message": "Window is now transparent"}
        except Exception as e:
            return {"success": False, "message": f"Failed to make window transparent: {str(e)}"}
    
    def restore_window(self):
        """Restore window from transparent state"""
        try:
            if not self.is_transparent:
                return {"success": True, "message": "Window is already visible"}
                
            window = webview.windows[0]
            hwnd = win32gui.FindWindow(None, window.title)
            
            if not hwnd:
                return {"success": False, "message": "Could not find window"}
            
            # Get current extended style
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # Remove the WS_EX_TRANSPARENT flag to make window clickable again
            if ex_style & win32con.WS_EX_TRANSPARENT:
                win32gui.SetWindowLong(
                    hwnd, 
                    win32con.GWL_EXSTYLE,
                    ex_style & ~win32con.WS_EX_TRANSPARENT
                )
            
            # Make fully opaque again (alpha = 255)
            ctypes.windll.user32.SetLayeredWindowAttributes(
                hwnd, 0, 255, win32con.LWA_ALPHA
            )
            
            # If we have saved position, ensure it's in the right place
            if self.original_window_pos:
                x, y, right, bottom = self.original_window_pos
                width = right - x
                height = bottom - y
                
                # Make sure it's in the right position without stealing focus
                win32gui.SetWindowPos(
                    hwnd, 
                    0,  # hWndInsertAfter - no change in z-order
                    x, y, width, height, 
                    win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER
                )
            
            self.is_transparent = False
            
            return {"success": True, "message": "Window restored without focus"}
        except Exception as e:
            return {"success": False, "message": f"Failed to restore window: {str(e)}"}
