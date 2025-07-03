import json
import time
import threading
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.app_utils import resource_path
from utils.path_utils import find_system_chromedriver

# Ensure Selenium Manager is disabled for this module
os.environ['SE_DISABLE_SELENIUM_MANAGER'] = '1'

class HARCapture:
    def __init__(self):
        self.driver = None
        self.har_data = {"log": {"entries": []}}
        self.capturing = False
        self.capture_thread = None
        self.completed = False
        self.browser_closed_callback = None
        
    def setup_driver(self):
        """Set up Chrome driver with HAR capture capabilities"""
        chrome_options = Options()
        
        # Essential stealth arguments (less aggressive)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance and compatibility arguments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        
        # User agent spoofing with latest Chrome version
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        
        # Minimal prefs to avoid breaking functionality
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Enable performance logging to capture network requests
        chrome_options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        # Use chromedriver from the system
        chromedriver_path = find_system_chromedriver()
        if not chromedriver_path:
            raise Exception("ChromeDriver not found. Please install Chrome or download ChromeDriver.")
        
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Minimal stealth JavaScript injection
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override plugins to look more realistic
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', description: 'Portable Document Format'},
                        {name: 'Chrome PDF Viewer', description: 'PDF Viewer'},
                        {name: 'Native Client', description: 'Native Client'}
                    ]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """
        })
        
        # Enable Network domain for DevTools
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        print("Chrome driver initialized successfully")
        
    def start_capture(self):
        """Start capturing network requests"""
        self.capturing = True
        print("HAR capture started. All network requests will be recorded.")
        
    def get_network_logs(self):
        """Get network logs from Chrome DevTools"""
        logs = self.driver.get_log('performance')
        return logs
    
    def get_cookies(self):
        """Get all cookies from the current session"""
        try:
            cookies = self.driver.get_cookies()
            return cookies
        except Exception as e:
            print(f"Error getting cookies: {e}")
            return []
        
    def process_network_logs(self):
        """Process and add network logs to HAR data"""
        if not self.capturing:
            return
            
        logs = self.get_network_logs()
        
        for log in logs:
            message = log.get('message', {})
            if isinstance(message, str):
                try:
                    message = json.loads(message)
                except json.JSONDecodeError:
                    continue
                    
            log_message = message.get('message', {})
            method = log_message.get('method', '')
            params = log_message.get('params', {})
            
            # Process network request events - simplified approach
            if method == 'Network.requestWillBeSent':
                self._process_request_will_be_sent(params)
            elif method == 'Network.responseReceived':
                self._process_response_received(params)
    
    def _process_request_will_be_sent(self, params):
        """Process Network.requestWillBeSent events"""
        request = params.get('request', {})
        request_id = params.get('requestId', '')
        timestamp = params.get('timestamp', time.time())
        
        # Get current cookies
        cookies = self.get_cookies()
        
        # Create HAR entry for request
        har_entry = {
            "startedDateTime": datetime.fromtimestamp(timestamp).isoformat() + "Z",
            "time": 0,
            "request": {
                "method": request.get('method', 'GET'),
                "url": request.get('url', ''),
                "httpVersion": "HTTP/1.1",
                "headers": self._format_headers(request.get('headers', {})),
                "queryString": self._parse_query_string(request.get('url', '')),
                "cookies": self._format_cookies(cookies),
                "headersSize": -1,
                "bodySize": 0
            },
            "response": {
                "status": 0,
                "statusText": "",
                "httpVersion": "HTTP/1.1",
                "headers": [],
                "cookies": [],
                "content": {
                    "size": 0,
                    "mimeType": "text/html"
                },
                "redirectURL": "",
                "headersSize": -1,
                "bodySize": -1
            },
            "cache": {},
            "timings": {
                "blocked": 0,
                "dns": -1,
                "ssl": -1,
                "connect": -1,
                "send": 0,
                "wait": 0,
                "receive": 0
            },
            "pageref": "page_1",
            "_requestId": request_id
        }
        
        # Add request body if present
        if request.get('postData'):
            post_data = request.get('postData', '')
            har_entry["request"]["postData"] = {
                "mimeType": request.get('headers', {}).get('content-type', 'text/plain'),
                "text": post_data
            }
            har_entry["request"]["bodySize"] = len(post_data)
        
        self.har_data["log"]["entries"].append(har_entry)
        
        # Print authorization headers if present
        headers = request.get('headers', {})
        for header_name, header_value in headers.items():
            if 'authorization' in header_name.lower() or 'bearer' in str(header_value).lower():
                print(f"Authorization header found: {header_name}: {header_value}")
            
    def _process_response_received(self, params):
        """Process Network.responseReceived events"""
        response = params.get('response', {})
        request_id = params.get('requestId', '')
        
        # Find matching request entry and update response
        for entry in reversed(self.har_data["log"]["entries"]):
            if entry.get("_requestId") == request_id:
                entry["response"]["status"] = response.get('status', 0)
                entry["response"]["statusText"] = response.get('statusText', '')
                entry["response"]["headers"] = self._format_headers(response.get('headers', {}))
                entry["response"]["content"]["mimeType"] = response.get('mimeType', 'text/html')
                break
                            
    def _format_headers(self, headers_dict):
        """Format headers dictionary to HAR format"""
        formatted_headers = []
        for name, value in headers_dict.items():
            formatted_headers.append({
                "name": name,
                "value": str(value)
            })
        return formatted_headers
    
    def _format_cookies(self, cookies_list):
        """Format cookies list to HAR format"""
        formatted_cookies = []
        for cookie in cookies_list:
            formatted_cookies.append({
                "name": cookie.get('name', ''),
                "value": cookie.get('value', ''),
                "path": cookie.get('path', '/'),
                "domain": cookie.get('domain', ''),
                "expires": cookie.get('expiry', ''),
                "httpOnly": cookie.get('httpOnly', False),
                "secure": cookie.get('secure', False)
            })
        return formatted_cookies
    
    def _parse_query_string(self, url):
        """Parse query string from URL"""
        if '?' not in url:
            return []
        
        query_string = url.split('?', 1)[1]
        params = []
        
        for param in query_string.split('&'):
            if '=' in param:
                name, value = param.split('=', 1)
                params.append({
                    "name": name,
                    "value": value
                })
        
        return params
                
    def save_har_file(self, filename=None):
        """Save HAR data to file"""
        try:
            if filename is None:
                # Create har_and_cookies folder in the current working directory
                har_dir = os.path.join(os.getcwd(), "har_and_cookies")
                filename = os.path.join(har_dir, "copilot.microsoft.com.har")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Clean up entries by removing internal _requestId field
            cleaned_entries = []
            for entry in self.har_data["log"]["entries"]:
                cleaned_entry = entry.copy()
                if "_requestId" in cleaned_entry:
                    del cleaned_entry["_requestId"]
                cleaned_entries.append(cleaned_entry)
            
            # Add HAR metadata
            har_output = {
                "log": {
                    "version": "1.2",
                    "creator": {
                        "name": "HAR Capture Script",
                        "version": "1.0"
                    },
                    "pages": [
                        {
                            "startedDateTime": datetime.now().isoformat() + "Z",
                            "id": "page_1",
                            "title": "Copilot Session",
                            "pageTimings": {
                                "onContentLoad": -1,
                                "onLoad": -1
                            }
                        }
                    ],
                    "entries": cleaned_entries
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(har_output, f, indent=2, ensure_ascii=False)
            
            print(f"HAR file saved: {filename}")
            print(f"Total network requests captured: {len(cleaned_entries)}")
            
            # Print summary of captured data
            auth_count = 0
            post_count = 0
            for entry in cleaned_entries:
                # Count authorization headers
                for header in entry["request"]["headers"]:
                    if 'authorization' in header["name"].lower():
                        auth_count += 1
                        break
                # Count POST requests with data
                if entry["request"]["method"] == "POST" and entry["request"].get("postData"):
                    post_count += 1
            
            print(f"Requests with authorization headers: {auth_count}")
            print(f"POST requests with payload: {post_count}")
            print(f"Total cookies captured: {sum(len(entry['request']['cookies']) for entry in cleaned_entries)}")
            
            return True
            
        except Exception as e:
            print(f"Error saving HAR file: {e}")
            return False
            
    def enhance_stealth(self):
        """Apply additional stealth measures after page load"""
        try:
            # Minimal stealth enhancement - just remove webdriver traces
            self.driver.execute_script("""
                // Remove webdriver from window
                delete window.webdriver;
                
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                // Clean up any automation remnants
                window.navigator.webdriver = undefined;
            """)
            
            # Set a realistic viewport
            self.driver.set_window_size(1920, 1080)
            
            print("Lightweight stealth measures applied")
            
        except Exception as e:
            print(f"Warning: Could not apply stealth enhancement: {e}")

    def set_browser_closed_callback(self, callback):
        """Set callback function to be called when browser closes unexpectedly"""
        self.browser_closed_callback = callback

    def _is_browser_alive(self):
        """Check if the browser is still alive"""
        try:
            if self.driver is None:
                return False
            # Try to get the current URL to check if browser is responsive
            self.driver.current_url
            # Also check window handles
            self.driver.window_handles
            return True
        except Exception as e:
            # Common exceptions when browser is closed
            error_msg = str(e).lower()
            if any(phrase in error_msg for phrase in [
                'chrome not reachable', 'no such window', 'target window already closed',
                'connection refused', 'session deleted', 'invalid session id'
            ]):
                return False
            # For other exceptions, assume browser is still alive
            return True

    def start_background_capture(self):
        """Start HAR capture in background thread"""
        def capture_loop():
            try:
                print("Setting up Chrome driver for HAR capture...")
                self.setup_driver()
                
                print("Navigating to Copilot...")
                self.driver.get("https://copilot.microsoft.com")
                
                # Apply enhanced stealth measures after page load
                time.sleep(2)
                self.enhance_stealth()
                
                print("HAR capture started. Browser is ready for use.")
                
                # Start HAR capture
                self.start_capture()
                
                # Keep processing network logs until completed
                while not self.completed:
                    try:
                        # Check if browser is still alive
                        if not self._is_browser_alive():
                            print("Browser was closed by user")
                            self.completed = True
                            # Notify UI that browser was closed unexpectedly
                            if self.browser_closed_callback:
                                self.browser_closed_callback()
                            break
                            
                        time.sleep(2)  # Process logs every 2 seconds
                        self.process_network_logs()
                    except Exception as e:
                        error_msg = str(e).lower()
                        print(f"Error processing logs: {e}")
                        # Check if it's a browser connection error
                        if any(phrase in error_msg for phrase in [
                            'chrome not reachable', 'no such window', 'target window already closed',
                            'connection refused', 'session deleted', 'invalid session id'
                        ]):
                            print("Browser connection lost")
                            self.completed = True
                            if self.browser_closed_callback:
                                self.browser_closed_callback()
                        break
                        
            except Exception as e:
                print(f"Error in HAR capture: {e}")
                
        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        
        return True
        
    def complete_capture(self):
        """Complete the HAR capture and save the file"""
        try:
            self.completed = True
            
            # Final processing of network logs
            self.process_network_logs()
            
            # Save the HAR file
            success = self.save_har_file()
            
            # Close the browser
            if self.driver:
                print("Closing browser...")
                self.driver.quit()
                self.driver = None
            
            return success
            
        except Exception as e:
            print(f"Error completing HAR capture: {e}")
            return False
            
    def cleanup(self):
        """Clean up resources"""
        try:
            self.completed = True
            if self.driver:
                self.driver.quit()
                self.driver = None
        except:
            pass

    def is_active(self):
        """Check if HAR capture is currently active"""
        return self.capturing and not self.completed and self._is_browser_alive()

    def is_browser_open(self):
        """Check if browser is currently open"""
        return self.driver is not None and self._is_browser_alive()

# Global instance for the API
_har_capture_instance = None

def get_har_capture_instance():
    """Get or create the HAR capture instance"""
    global _har_capture_instance
    if _har_capture_instance is None:
        _har_capture_instance = HARCapture()
    return _har_capture_instance

def cleanup_har_capture():
    """Clean up the HAR capture instance"""
    global _har_capture_instance
    if _har_capture_instance:
        _har_capture_instance.cleanup()
        _har_capture_instance = None
