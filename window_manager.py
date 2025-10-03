"""
Window management module for handling application windows.
"""

import time
import subprocess
import psutil
import pyautogui
import pygetwindow as gw
import os
from typing import Optional, List, Tuple, Dict, Any


class WindowManager:
    """
    Manages application windows including launching, focusing, and positioning.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the window manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.current_window = None
        self.app_name = None
        self.app_path = None
        self.startup_delay = 3
    
    def set_app(self, app_name: str) -> bool:
        """
        Set the current application to manage.
        
        Args:
            app_name (str): Name of the application
            
        Returns:
            bool: True if app configuration loaded successfully, False otherwise
        """
        try:
            app_config = self.config_manager.get_app_config(app_name)
            self.app_name = app_name
            self.app_path = app_config["path"]
            self.startup_delay = app_config.get("startup_delay", 3)
            return True
        except ValueError as e:
            print(f"Error setting app: {e}")
            return False
    
    
    def get_existing_windows(self) -> List[Any]:
        """
        Get existing windows for the current application.
        
        Returns:
            list: List of existing windows
        """
        if not self.app_name:
            return []
        
        try:
            return gw.getWindowsWithTitle(self.app_name)
        except Exception as e:
            print(f"Error getting existing windows: {e}")
            return []
    
    def launch_app(self, max_retries: int = 3) -> bool:
        """
        Launch the application if it's not already running, or use existing instance.
        
        Args:
            max_retries (int): Maximum number of launch attempts
            
        Returns:
            bool: True if app is available (launched or existing), False otherwise
        """
        if not self.app_name or not self.app_path:
            print("No app configured for launching")
            return False
        
        # Check for existing windows first
        existing_windows = self.get_existing_windows()
        if existing_windows:
            print(f"{self.app_name} window already exists - using existing instance")
            self.current_window = existing_windows[0]
            return True
        
        # Check if app is already running
        from main import is_app_running_standalone
        if is_app_running_standalone(self.app_name):
            print(f"{self.app_name} is already running - using existing instance")
            return True
        
        # Launch the application only if not already running
        print(f"Launching {self.app_name}...")
        try:
            subprocess.Popen([self.app_path])
            print(f"Launched: {self.app_path}")
            time.sleep(self.startup_delay)
            
            # Verify launch was successful
            if self._verify_app_launched():
                return True
            else:
                print(f"Launch verification failed")
                return False
                
        except Exception as e:
            print(f"Error launching app: {e}")
            return False
    
    def _verify_app_launched(self) -> bool:
        """
        Verify that the application launched successfully.
        
        Returns:
            bool: True if app launched successfully, False otherwise
        """
        # Give the app a moment to start
        time.sleep(2)
        
        # Check if window exists (more reliable than process check)
        windows = self.get_existing_windows()
        if not windows:
            print("App window not found")
            return False
        
        self.current_window = windows[0]
        print(f"App launched successfully: {self.current_window.title}")
        return True
    
    def focus_window(self) -> bool:
        """
        Find and focus the application window.
        
        Returns:
            bool: True if window was focused successfully, False otherwise
        """
        if not self.app_name:
            print("No app configured for window focusing")
            return False
        
        windows = self.get_existing_windows()
        if not windows:
            print(f"{self.app_name} window not found")
            return False
        
        self.current_window = windows[0]
        
        try:
            # Try to activate the window
            self.current_window.activate()
            time.sleep(0.5)
            print(f"Window activated: {self.current_window.title}")
        except Exception as e:
            print(f"Window activation failed: {e}")
            # Try alternative approach
            try:
                self.current_window.minimize()
                time.sleep(0.5)
                self.current_window.restore()
                time.sleep(0.5)
                print(f"Window restored: {self.current_window.title}")
            except Exception as e2:
                print(f"Window restore failed: {e2}")
                return False
        
        # Move window to primary monitor
        try:
            window_pos = self.config_manager.get_window_position()
            self.current_window.moveTo(window_pos["x"], window_pos["y"])
            time.sleep(0.5)
            print("Window moved to primary monitor")
        except Exception as e:
            print(f"Failed to move window: {e}")
        
        return True
    
    def maximize_window(self) -> bool:
        """
        Maximize the current window using keyboard shortcuts.
        
        Returns:
            bool: True if window was maximized successfully, False otherwise
        """
        if not self.current_window:
            print("No current window to maximize")
            return False
        
        try:
            # Use keyboard shortcut to maximize
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.5)
            pyautogui.press('x')
            time.sleep(0.5)
            print("Window maximized via keyboard")
            return True
        except Exception as e:
            print(f"Error maximizing window: {e}")
            return False
    
    def verify_window_maximized(self) -> bool:
        """
        Verify that the window is maximized by checking dimensions and template matching.
        
        Returns:
            bool: True if window is maximized, False otherwise
        """
        if not self.current_window:
            return False
        
        try:
            # Get window dimensions
            window_rect = self.current_window._rect
            screen_width, screen_height = pyautogui.size()
            
            # Check if window takes up most of the screen
            window_width = window_rect.width
            window_height = window_rect.height
            
            # Consider maximized if window takes up at least 80% of screen (more lenient)
            width_ratio = window_width / screen_width
            height_ratio = window_height / screen_height
            
            is_maximized = width_ratio >= 0.8 and height_ratio >= 0.8
            
            if is_maximized:
                print("Window verification: Maximized")
            else:
                print(f"Window verification: Not maximized (size: {window_width}x{window_height})")
            
            # Additional template matching verification for app-specific elements
            if is_maximized and self._verify_app_ready_with_templates():
                print("Template verification: App is ready and visible")
                return True
            elif is_maximized:
                print("Template verification: App window maximized but content not verified")
                return True  # Still return True if dimensions are correct
            else:
                return False
            
        except Exception as e:
            print(f"Error verifying window maximized: {e}")
            return False
    
    def _verify_app_ready_with_templates(self) -> bool:
        """
        Verify app is ready using template matching for app-specific elements.
        
        Returns:
            bool: True if app-specific elements are found, False otherwise
        """
        try:
            from ui_detection import UIDetector
            ui_detector = UIDetector(self.config_manager)
            
            # Get app-specific verification templates from config
            verification_templates = self.config_manager.get_verification_templates(self.app_name)
            
            if not verification_templates:
                print("No verification templates configured - skipping template verification")
                return True  # Return True if no templates configured
            
            print(f"Verifying app readiness with {len(verification_templates)} templates...")
            
            # Check each template
            for template_path in verification_templates:
                if not os.path.exists(template_path):
                    print(f"Template not found: {template_path}")
                    continue
                
                # Try to find the template
                match = ui_detector.find_template(template_path, threshold=0.7)
                if match:
                    print(f"Found verification template: {os.path.basename(template_path)}")
                    return True
                else:
                    print(f"Template not found: {os.path.basename(template_path)}")
            
            print("No verification templates found - app may not be ready")
            return False
            
        except Exception as e:
            print(f"Error in template verification: {e}")
            return False
    
    def prepare_application(self, max_retries: int = 3) -> bool:
        """
        Complete application preparation process.
        
        Args:
            max_retries (int): Maximum number of retries for each step
            
        Returns:
            bool: True if application is prepared successfully, False otherwise
        """
        print(f"Preparing application: {self.app_name}")
        
        # Step 1: Launch application
        if not self.launch_app(max_retries):
            print("Failed to launch application")
            return False
        
        # Step 2: Focus window
        if not self.focus_window():
            print("Failed to focus window")
            return False
        
        # Step 3: Maximize window
        if not self.maximize_window():
            print("Failed to maximize window")
            return False
        
        # Step 4: Verify maximization
        if not self.verify_window_maximized():
            print("Window maximization verification failed")
            return False
        
        print(f"Application {self.app_name} prepared successfully!")
        return True
    
    def get_window_info(self) -> Dict[str, Any]:
        """
        Get information about the current window.
        
        Returns:
            dict: Window information
        """
        if not self.current_window:
            return {}
        
        try:
            rect = self.current_window._rect
            return {
                "title": self.current_window.title,
                "x": rect.left,
                "y": rect.top,
                "width": rect.width,
                "height": rect.height,
                "is_maximized": self.verify_window_maximized()
            }
        except Exception as e:
            print(f"Error getting window info: {e}")
            return {}
    
    def close_window(self) -> bool:
        """
        Close the current window.
        
        Returns:
            bool: True if window was closed successfully, False otherwise
        """
        if not self.current_window:
            print("No current window to close")
            return False
        
        try:
            self.current_window.close()
            self.current_window = None
            print("Window closed successfully")
            return True
        except Exception as e:
            print(f"Error closing window: {e}")
            return False
