# Screen Capture Tool - Windows Native App

A modern Windows native application for capturing screen areas, built with Python and web technologies. The app is **hidden from all screen capture** using Windows Display Affinity.

## Features

- 🖥️ **Native Windows App** - Real Windows application, not just a web browser
- 🔒 **Screen Capture Protection** - Hidden from screenshots and screen recordings
- 🎯 **Area Selection** - Click two corners to select any screen area
- 🌐 **Modern UI** - Beautiful HTML/CSS/JS interface
- 🔗 **Python Integration** - JavaScript can call Python functions seamlessly
- 📸 **Screenshot Management** - View and delete captured screenshots
- ⌨️ **Keyboard Shortcuts** - Ctrl+S to start, Escape to cancel, F5 to refresh

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python webview_app.py
   ```

## How to Use

1. Click **"Start Capture"** button
2. Right-click the **first corner** of the area you want to capture
3. Right-click the **second corner** of the area
4. **Release the mouse** to capture the screenshot
5. The screenshot will be saved with a timestamp

## Architecture

### Python Backend (`webview_app.py`)
- **ScreenCaptureAPI**: Main API class exposing Python functions to JavaScript
- **Window Affinity**: Uses Windows API to hide from screen capture
- **Mouse Listening**: Global mouse click detection using pynput
- **Screenshot Capture**: Uses pyautogui for screen capture

### Frontend (HTML/CSS/JS)
- **Modern UI**: Glassmorphism design with gradients and blur effects
- **Responsive**: Adapts to different window sizes
- **Interactive**: Real-time status updates and controls
- **File Management**: List and delete screenshots

### Communication
JavaScript ↔ Python communication happens through:
```javascript
// JavaScript calling Python
const result = await pywebview.api.start_capture();

// Python calling JavaScript
webview.windows[0].evaluate_js('updateStatus("message", "type")')
```

## Key Technologies

- **pywebview**: Creates native Windows apps with web UI
- **pynput**: Global mouse and keyboard monitoring
- **pyautogui**: Screen capture functionality
- **Windows API**: Screen capture protection via ctypes

## Security Features

The application uses Windows Display Affinity (`WDA_EXCLUDEFROMCAPTURE`) to:
- Hide the window from screenshots
- Prevent screen recording of the app
- Protect sensitive UI elements
- Maintain privacy during screen sharing

## File Structure

```
screen-ai/
├── webview_app.py          # Main Python application
├── requirements.txt        # Python dependencies
├── ui/
│   ├── index.html         # Main HTML interface
│   ├── styles.css         # Modern CSS styling
│   └── script.js          # JavaScript functionality
└── screenshot_*.png       # Captured screenshots
```

## Keyboard Shortcuts

- **Ctrl+S**: Start capture
- **Escape**: Cancel current capture
- **F5**: Refresh screenshots list

## Customization

You can easily customize:
- **UI Design**: Edit `ui/styles.css` for different themes
- **Functionality**: Add new Python functions in `ScreenCaptureAPI`
- **Shortcuts**: Modify keyboard shortcuts in `ui/script.js`
- **Window Properties**: Adjust size, position, and behavior in `create_app()`
