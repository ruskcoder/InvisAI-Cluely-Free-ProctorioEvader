import tkinter as tk
from tkinter import ttk
import os
import sys
import ctypes


def create_loading_window():
    """Create a loading splash screen"""

    root = tk.Tk()
    root.title("Loading InvisAI")
    root.overrideredirect(True) 
    root.configure(bg='#36394a')

    # Set window size
    window_width = 300
    window_height = 150

    # Center the window on screen, accounting for Windows display scaling
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    print(f"Screen size: {screen_width}x{screen_height}")
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

    # Adjust for Windows scaling
    x = int((screen_width - window_width) // 2)
    y = int((screen_height - window_height) // 2)
    x = int(x * scaleFactor)
    y = int(y * scaleFactor)

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Make window always on top
    root.attributes('-topmost', True)

    # Main frame
    main_frame = tk.Frame(root, bg='#36394a', padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)

    # Content frame for side-by-side layout
    content_frame = tk.Frame(main_frame, bg='#36394a')
    content_frame.pack(expand=True)

    # Try to load the eye icon
    try:
        # For development and PyInstaller
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, 'google-eye.png')
        else:
            base_path = os.path.dirname(__file__)
            icon_path = os.path.join(os.path.dirname(base_path), 'google-eye.png')
        if os.path.exists(icon_path):
            # Load and display icon
            from PIL import Image, ImageTk
            img = Image.open(icon_path)
            img = img.resize((72, 72), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            icon_label = tk.Label(content_frame, image=photo, bg='#36394a')
            icon_label.image = photo  # Keep a reference
            icon_label.pack(side='left', padx=(0, 15))
        else:
            print(f"Icon file not found: {icon_path}")
            icon_label = tk.Label(content_frame, text="👁", font=('Arial', 48), fg='white', bg='#36394a')
            icon_label.pack(side='left', padx=(0, 15))
    except ImportError:
        # If PIL not available, use text icon
        icon_label = tk.Label(content_frame, text="👁", font=('Arial', 48), fg='white', bg='#36394a')
        icon_label.pack(side='left', padx=(0, 15))

    # Text frame for app name
    text_frame = tk.Frame(content_frame, bg='#36394a')
    text_frame.pack(side='left', fill='y', expand=True)

    # App name - centered vertically
    name_label = tk.Label(text_frame, text="InvisAI", font=('Segoe UI', 20, 'bold'), fg='white', bg='#36394a')
    name_label.pack(expand=True)

    # Progress bar style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Loading.Horizontal.TProgressbar", 
                   background='#5863f4',
                   troughcolor='#2d3037',
                   borderwidth=0,
                   relief='flat',
                   lightcolor='#5863f4',
                   darkcolor='#5863f4')

    # Remove focus border and selection border
    style.map("Loading.Horizontal.TProgressbar",
             bordercolor=[('focus', '#5863f4')],
             focuscolor=[('focus', '#5863f4')])

    # Progress bar below the content
    progress = ttk.Progressbar(main_frame, style="Loading.Horizontal.TProgressbar", 
                              mode='indeterminate', length=200)
    progress.pack(pady=(15, 0))
    progress.start(10)

    return root, progress

def close_loading_window(root):
    """Close the loading window"""
    try:
        root.quit()
        root.destroy()
    except:
        pass
