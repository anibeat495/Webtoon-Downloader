"""
PacketSDK Integration Module
Handles PacketSDK initialization and management
"""
import os
import sys
import subprocess
import platform
import threading
import time
from pathlib import Path


class PacketSDKManager:
    """Manages PacketSDK integration for monetization"""
    
    def __init__(self, appkey, log_callback=None):
        """
        Initialize PacketSDK Manager
        
        Args:
            appkey (str): Your PacketSDK application key
            log_callback (callable, optional): Callback for logging
        """
        self.appkey = appkey
        self.log_callback = log_callback
        self.sdk_process = None
        self.is_running = False
        self.sdk_path = self._get_sdk_path()
        
    def log(self, message, level="INFO"):
        """Log message if callback is set"""
        if self.log_callback:
            self.log_callback(message, level)
    
    def _get_sdk_path(self):
        """Get the appropriate SDK executable path based on system architecture"""
        try:
            # Get the directory - handle both script and frozen (PyInstaller) modes
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_dir = Path(sys._MEIPASS)
            else:
                # Running as script
                base_dir = Path(__file__).parent.parent
            
            sdk_dir = base_dir / "packet_sdk_win-1.0.4" / "bin"
            
            # Detect system architecture
            is_64bit = sys.maxsize > 2**32 or platform.machine().endswith('64')
            
            if is_64bit:
                sdk_exe = sdk_dir / "win64" / "packet_sdk.exe"
            else:
                sdk_exe = sdk_dir / "win32" / "packet_sdk.exe"
            
            if sdk_exe.exists():
                return str(sdk_exe.absolute())
            else:
                self.log(f"PacketSDK executable not found at: {sdk_exe}", "WARNING")
                return None
                
        except Exception as e:
            self.log(f"Error locating PacketSDK: {str(e)}", "ERROR")
            return None
    
    def start(self):
        """Start PacketSDK as a subprocess"""
        if self.is_running:
            self.log("PacketSDK is already running", "WARNING")
            return True
        
        if not self.sdk_path:
            self.log("PacketSDK path not found, skipping monetization", "WARNING")
            return False
        
        if not self.appkey:
            self.log("PacketSDK appkey not set, skipping monetization", "WARNING")
            return False
        
        try:
            # Start PacketSDK as subprocess
            self.log("Starting PacketSDK for monetization...", "INFO")
            
            # Create startupinfo to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Start the SDK with appkey
            self.sdk_process = subprocess.Popen(
                [self.sdk_path, f"-appkey={self.appkey}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.is_running = True
            
            # Start monitor thread to check SDK status
            monitor_thread = threading.Thread(target=self._monitor_sdk, daemon=True)
            monitor_thread.start()
            
            self.log("PacketSDK started successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to start PacketSDK: {str(e)}", "ERROR")
            return False
    
    def _monitor_sdk(self):
        """Monitor SDK process and log output"""
        if not self.sdk_process:
            return
        
        try:
            # Monitor for initial success messages
            start_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            while time.time() - start_time < timeout:
                if self.sdk_process.poll() is not None:
                    # Process ended
                    self.log("PacketSDK process ended unexpectedly", "WARNING")
                    self.is_running = False
                    break
                
                time.sleep(1)
            
            # If still running after timeout, consider it successful
            if self.sdk_process and self.sdk_process.poll() is None:
                self.log("PacketSDK is running in background", "INFO")
                
        except Exception as e:
            self.log(f"Error monitoring PacketSDK: {str(e)}", "ERROR")
    
    def stop(self):
        """Stop PacketSDK"""
        if not self.is_running:
            return
        
        try:
            if self.sdk_process:
                self.log("Stopping PacketSDK...", "INFO")
                self.sdk_process.terminate()
                
                # Wait for process to end (with timeout)
                try:
                    self.sdk_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if not terminated
                    self.sdk_process.kill()
                
                self.sdk_process = None
                self.is_running = False
                self.log("PacketSDK stopped", "INFO")
                
        except Exception as e:
            self.log(f"Error stopping PacketSDK: {str(e)}", "ERROR")
    
    def get_status(self):
        """Get current SDK status"""
        if not self.is_running:
            return "Not Running"
        
        if self.sdk_process and self.sdk_process.poll() is None:
            return "Running"
        else:
            self.is_running = False
            return "Stopped"


# Import configuration from config file
try:
    import sys
    from pathlib import Path
    # Add parent directory to path to import config
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    from packet_sdk_config import PACKET_SDK_APPKEY, PACKET_SDK_ENABLED
except ImportError:
    # Fallback if config file not found
    PACKET_SDK_APPKEY = "your_appkey_here"
    PACKET_SDK_ENABLED = True
    print("Warning: packet_sdk_config.py not found, using default configuration")
