#!/usr/bin/env python3
"""
The Dying Lands - Desktop Application
Launches the hexcrawl generator in a native WebView window.
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
import webview
from flask import Flask

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from ascii_map_viewer import app

class HexcrawlApp:
    def __init__(self):
        self.flask_thread = None
        self.flask_app = app
        self.host = '127.0.0.1'
        self.port = 5000
        self.url = f'http://{self.host}:{self.port}'
        
    def start_flask(self):
        """Start the Flask application in a separate thread."""
        self.flask_app.run(
            host=self.host,
            port=self.port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    
    def wait_for_flask(self, timeout=10):
        """Wait for Flask to be ready."""
        import requests
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.url, timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.1)
        return False
    
    def on_window_loaded(self):
        """Called when the WebView window is loaded."""
        print("The Dying Lands - Desktop Application loaded successfully!")
    
    def on_window_closing(self):
        """Called when the WebView window is closing."""
        print("Shutting down The Dying Lands application...")
        # Note: Flask will be terminated when the main process ends
        return True

def main():
    """Main entry point for the desktop application."""
    print("Starting The Dying Lands - Desktop Application...")
    
    # Create the application instance
    hexcrawl_app = HexcrawlApp()
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=hexcrawl_app.start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to be ready
    print("Starting web server...")
    if not hexcrawl_app.wait_for_flask():
        print("Error: Could not start the web server!")
        sys.exit(1)
    
    print(f"Web server started at {hexcrawl_app.url}")
    
    # Create and configure the WebView window
    window_config = {
        'title': 'The Dying Lands - Hexcrawl Generator',
        'url': hexcrawl_app.url,
        'width': 1200,
        'height': 800,
        'min_size': (800, 600),
        'resizable': True,
        'fullscreen': False,
        'minimized': False,
        'on_top': False,
        'shadow': True,
        'focus': True
    }
    
    # Add event handlers
    def on_loaded():
        hexcrawl_app.on_window_loaded()
    
    def on_closing():
        return hexcrawl_app.on_window_closing()
    
    # Create the WebView window
    try:
        webview.create_window(
            title=window_config['title'],
            url=window_config['url'],
            width=window_config['width'],
            height=window_config['height'],
            min_size=window_config['min_size'],
            resizable=window_config['resizable'],
            fullscreen=window_config['fullscreen'],
            minimized=window_config['minimized'],
            on_top=window_config['on_top'],
            shadow=window_config['shadow'],
            focus=window_config['focus']
        )
        
        # Set event handlers
        webview.start(
            debug=False,
            http_server=False,  # We're using our own Flask server
            user_agent='The Dying Lands Desktop App/1.0'
        )
        
    except Exception as e:
        print(f"Error creating WebView window: {e}")
        print("Falling back to browser...")
        webbrowser.open(hexcrawl_app.url)
        
        # Keep the Flask server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)

if __name__ == '__main__':
    main()