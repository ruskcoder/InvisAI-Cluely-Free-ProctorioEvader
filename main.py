import webview
import os
from screen_capture_api import ScreenCaptureAPI
from window_manager import windowCreated


def createApp():
    htmlFile = os.path.join(os.path.dirname(__file__), 'ui', 'index.html')
    api = ScreenCaptureAPI()
    window = webview.create_window(
        'Screen Capture Tool',
        htmlFile,
        js_api=api,
        width=300,
        height=400,
        # min_size=(350, 500),
        on_top=True,
        shadow=True,
    )
    webview.start(windowCreated, debug=False)


if __name__ == '__main__':
    print("Starting application...")
    createApp()
