"""
UI detection module for template matching and OCR operations.
"""

import time
import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple, List, Dict, Any
import os


class UIDetector:
    """
    Handles UI element detection through template matching and OCR.
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize the UI detector.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.screenshot_path = "screen.png"
        if config_manager:
            self.screenshot_path = config_manager.get_screenshot_path()
    
    def take_screenshot(self, save_path: str = None) -> str:
        """
        Take a screenshot of the current screen.
        
        Args:
            save_path (str, optional): Path to save the screenshot
            
        Returns:
            str: Path to the saved screenshot
        """
        if save_path is None:
            save_path = self.screenshot_path
        
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            print(f"Screenshot saved: {save_path}")
            return save_path
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return ""
    
    def find_template(self, template_path: str, threshold: float = 0.8, 
                     region: Tuple[int, int, int, int] = None) -> Optional[Tuple[int, int]]:
        """
        Find a template image on the screen using template matching.
        
        Args:
            template_path (str): Path to the template image
            threshold (float): Matching threshold (0.0 to 1.0)
            region (tuple, optional): Region to search in (x, y, width, height)
            
        Returns:
            tuple: (x, y) coordinates of the center of the match, or None if not found
        """
        if not os.path.exists(template_path):
            print(f"Template file not found: {template_path}")
            return None
        
        try:
            # Take screenshot
            screenshot_path = self.take_screenshot()
            if not screenshot_path:
                return None
            
            # Load images
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)
            
            if screenshot is None or template is None:
                print("Error loading images for template matching")
                return None
            
            # Crop region if specified
            if region:
                x, y, w, h = region
                screenshot = screenshot[y:y+h, x:x+w]
            
            # Convert to grayscale
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Calculate center coordinates
                template_h, template_w = template_gray.shape
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2
                
                # Adjust for region offset if region was specified
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                print(f"Template found at ({center_x}, {center_y}) with confidence {max_val:.2f}")
                return (center_x, center_y)
            else:
                print(f"Template not found (confidence: {max_val:.2f}, threshold: {threshold})")
                return None
                
        except Exception as e:
            print(f"Error in template matching: {e}")
            return None
    
    def click_at_location(self, location: Tuple[int, int], delay: float = 0.5) -> bool:
        """
        Click at the specified location.
        
        Args:
            location (tuple): (x, y) coordinates to click
            delay (float): Delay after clicking
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        try:
            x, y = location
            pyautogui.click(x, y)
            time.sleep(delay)
            print(f"Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Error clicking at location: {e}")
            return False
    
    def extract_text_from_region(self, region: List[int], 
                                screenshot_path: str = None) -> str:
        """
        Extract text from a specific region using OCR.
        
        Args:
            region (list): Region coordinates [x, y, width, height]
            screenshot_path (str, optional): Path to screenshot to use
            
        Returns:
            str: Extracted text
        """
        try:
            # For now, return placeholder text since OCR is not fully implemented
            # This would need to be replaced with actual OCR implementation
            print(f"OCR extraction from region {region} (placeholder)")
            return "placeholder_text"
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def verify_element_present(self, template_path: str, threshold: float = 0.8) -> bool:
        """
        Verify that a UI element is present on the screen.
        
        Args:
            template_path (str): Path to the template image
            threshold (float): Matching threshold
            
        Returns:
            bool: True if element is present, False otherwise
        """
        location = self.find_template(template_path, threshold)
        return location is not None
    
    def wait_for_element(self, template_path: str, timeout: int = 10, 
                        threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Wait for an element to appear on the screen.
        
        Args:
            template_path (str): Path to the template image
            timeout (int): Maximum time to wait in seconds
            threshold (float): Matching threshold
            
        Returns:
            tuple: (x, y) coordinates if found, None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            location = self.find_template(template_path, threshold)
            if location:
                return location
            time.sleep(0.5)
        
        print(f"Element not found within {timeout} seconds")
        return None
    
    def find_multiple_templates(self, template_paths: List[str], 
                              threshold: float = 0.8) -> List[Tuple[str, Tuple[int, int]]]:
        """
        Find multiple templates on the screen.
        
        Args:
            template_paths (list): List of template image paths
            threshold (float): Matching threshold
            
        Returns:
            list: List of (template_name, location) tuples
        """
        results = []
        
        for template_path in template_paths:
            location = self.find_template(template_path, threshold)
            if location:
                template_name = os.path.basename(template_path)
                results.append((template_name, location))
        
        return results
    
    def crop_and_ocr(self, region: List[int], save_crop: bool = False) -> str:
        """
        Crop a region from the screen and perform OCR on it.
        
        Args:
            region (list): Region coordinates [x, y, width, height]
            save_crop (bool): Whether to save the cropped image
            
        Returns:
            str: Extracted text
        """
        try:
            # Take screenshot first
            screenshot_path = self.take_screenshot()
            if not screenshot_path:
                return ""
            
            # Load and crop the image
            screenshot = cv2.imread(screenshot_path)
            x, y, w, h = region
            cropped = screenshot[y:y+h, x:x+w]
            
            if save_crop:
                crop_path = f"cropped_{int(time.time())}.png"
                cv2.imwrite(crop_path, cropped)
                print(f"Cropped image saved: {crop_path}")
            
            # For now, return placeholder since OCR is not fully implemented
            print(f"OCR on cropped region {region} (placeholder)")
            return "cropped_text"
            
        except Exception as e:
            print(f"Error in crop and OCR: {e}")
            return ""
    
    def detect_screen_change(self, previous_screenshot: str = None) -> bool:
        """
        Detect if the screen has changed by comparing screenshots.
        
        Args:
            previous_screenshot (str, optional): Path to previous screenshot
            
        Returns:
            bool: True if screen has changed, False otherwise
        """
        try:
            current_screenshot = self.take_screenshot()
            if not current_screenshot or not previous_screenshot:
                return True  # Assume change if no previous screenshot
            
            # Load images
            current = cv2.imread(current_screenshot)
            previous = cv2.imread(previous_screenshot)
            
            if current is None or previous is None:
                return True
            
            # Compare images
            diff = cv2.absdiff(current, previous)
            mean_diff = np.mean(diff)
            
            # Consider it changed if mean difference is above threshold
            threshold = 10  # Adjust as needed
            has_changed = mean_diff > threshold
            
            if has_changed:
                print(f"Screen change detected (diff: {mean_diff:.2f})")
            else:
                print(f"No significant screen change (diff: {mean_diff:.2f})")
            
            return has_changed
            
        except Exception as e:
            print(f"Error detecting screen change: {e}")
            return True  # Assume change on error
    
    def cleanup_screenshots(self):
        """Delete screenshot files to keep workspace clean."""
        try:
            screenshot_files = [
                "screen.png",
                "app_verification.png", 
                "template_match.png",
                "screenshot.png",
                "ocr_region.png"
            ]
            
            deleted_count = 0
            for screenshot_file in screenshot_files:
                if os.path.exists(screenshot_file):
                    os.remove(screenshot_file)
                    deleted_count += 1
                    print(f"Deleted screenshot: {screenshot_file}")
            
            if deleted_count > 0:
                print(f"✅ Cleaned up {deleted_count} screenshot files")
            else:
                print("No screenshot files to clean up")
                
        except Exception as e:
            print(f"Error cleaning up screenshots: {e}")

