"""
Workflow execution module for handling objectives and actions.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
try:
    from ui_detection import UIDetector
    from error_handler import ErrorHandler
except ImportError:
    # Handle import errors gracefully
    UIDetector = None
    ErrorHandler = None


class WorkflowExecutor:
    """
    Executes workflows based on objectives defined in configuration.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the workflow executor.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.ui_detector = UIDetector() if UIDetector else None
        self.error_handler = ErrorHandler(config_manager) if ErrorHandler else None
        self.current_objective = None
        self.action_history = []
        self.function_dispatcher = self._create_function_dispatcher()
    
    def _create_function_dispatcher(self) -> Dict[str, callable]:
        """
        Create a mapping between objective IDs and their corresponding functions.
        
        Returns:
            dict: Mapping of objective_id -> function
        """
        return {
            "notepad_basic_typing": self._execute_notepad_typing,
            "notepad_delete_and_close": self._execute_notepad_delete_close,
            "notepad_advanced_typing": self._execute_notepad_advanced_typing
        }
    
    def parse_objectives(self, objective_ids: List[str] = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse objectives from configuration and identify supported/unsupported ones.
        
        Args:
            objective_ids (list, optional): Specific objective IDs to parse
            
        Returns:
            tuple: (supported_objectives, unsupported_objectives)
        """
        return self.config_manager.get_objectives(objective_ids)
    
    def execute_objective(self, objective: Dict[str, Any]) -> bool:
        """
        Execute a single objective using function dispatcher or fallback to actions.
        
        Args:
            objective (dict): Objective configuration
            
        Returns:
            bool: True if objective completed successfully, False otherwise
        """
        self.current_objective = objective
        self.action_history = []
        
        objective_id = objective.get("id")
        objective_name = objective.get("name", "Unknown")
        
        print(f"Executing objective: {objective_name} ({objective_id})")
        print(f"App: {objective['app']}")
        
        # Check if objective is supported
        if not objective.get("supported", False):
            print(f"Objective '{objective_name}' is not supported")
            if self.error_handler:
                self.error_handler.send_notification(
                    f"Unsupported objective attempted: {objective_name}",
                    "error"
                )
            return False
        
        # Try function dispatcher first
        if objective_id in self.function_dispatcher:
            print(f"Using function dispatcher for: {objective_id}")
            try:
                function = self.function_dispatcher[objective_id]
                result = function()
                if result:
                    print(f"Objective '{objective_name}' completed via function dispatcher")
                    return True
                else:
                    print(f"Function dispatcher failed for: {objective_id}")
                    print("Falling back to objective actions...")
            except Exception as e:
                print(f"Function dispatcher error: {e}")
                print("Falling back to objective actions...")
        
        # Fallback to objective's own actions
        return self._execute_objective_actions(objective)
    
    def _execute_objective_actions(self, objective: Dict[str, Any]) -> bool:
        """
        Execute objective using individual actions (fallback method).
        
        Args:
            objective (dict): Objective configuration
            
        Returns:
            bool: True if objective executed successfully, False otherwise
        """
        actions = objective.get("actions", [])
        
        for i, action in enumerate(actions):
            print(f"Executing action {i+1}/{len(actions)}: {action['type']}")
            
            try:
                # Check prerequisites
                if not self._check_prerequisites(action):
                    print(f"Prerequisites not met for action: {action['type']}")
                    return False
                
                # Execute action
                success = self._execute_action(action)
                
                if not success:
                    # Handle action failure
                    return self.error_handler.handle_action_failure(
                        action, self.action_history, objective
                    )
                
                # Verify completion
                if not self._verify_action_completion(action):
                    print(f"Action verification failed: {action['type']}")
                    return False
                
                self.action_history.append(action)
                print(f"Action {i+1} completed successfully")
                
            except Exception as e:
                print(f"Error executing action {i+1}: {e}")
                return self.error_handler.handle_action_failure(
                    action, self.action_history, objective
                )
        
        print(f"Objective '{objective['name']}' completed successfully!")
        return True
    
    def _check_prerequisites(self, action: Dict[str, Any]) -> bool:
        """
        Check if prerequisites for an action are met.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if prerequisites are met, False otherwise
        """
        prerequisites = action.get("prerequisites", [])
        
        for prereq in prerequisites:
            if prereq == "app_maximized":
                # Check if app window is maximized using window manager
                try:
                    from window_manager import WindowManager
                    window_manager = WindowManager(self.config_manager)
                    if not window_manager.verify_window_maximized():
                        print("Prerequisite failed: app not maximized")
                        return False
                except Exception as e:
                    print(f"Warning: Could not verify app maximized: {e}")
                    # Continue anyway to avoid blocking automation
            elif prereq == "screen_open":
                # Check if correct screen is open
                if not self._is_correct_screen_open():
                    print("Prerequisite failed: incorrect screen open")
                    return False
            # Add more prerequisite checks as needed
        
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a single action.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if action executed successfully, False otherwise
        """
        action_type = action.get("type")
        
        if action_type == "type_text":
            return self._type_text(action)
        elif action_type == "click_element":
            return self._click_element(action)
        elif action_type == "verify_result":
            return self._verify_result(action)
        elif action_type == "hotkey":
            return self._hotkey(action)
        elif action_type == "key_press":
            return self._key_press(action)
        elif action_type == "delete_text":
            return self._delete_text(action)
        else:
            print(f"Unsupported action type: {action_type}")
            return False
    
    def _type_text(self, action: Dict[str, Any]) -> bool:
        """
        Type text into the application.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import pyautogui
            text = action.get("text", "")
            pyautogui.typewrite(text)
            time.sleep(0.5)  # Allow text to be processed
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def _click_element(self, action: Dict[str, Any]) -> bool:
        """
        Click on a UI element.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        method = action.get("method", "template_matching")
        
        if method == "template_matching":
            template_path = action.get("template")
            if template_path:
                location = self.ui_detector.find_template(template_path)
                if location:
                    return self.ui_detector.click_at_location(location)
        
        return False
    
    def _verify_result(self, action: Dict[str, Any]) -> bool:
        """
        Verify the result of an action.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        method = action.get("method", "ocr_text")
        expected_text = action.get("expected_text", "")
        region = action.get("region")
        
        if method == "ocr_text":
            detected_text = self.ui_detector.extract_text_from_region(region)
            return expected_text.lower() in detected_text.lower()
        
        return False
    
    def _verify_action_completion(self, action: Dict[str, Any]) -> bool:
        """
        Verify that an action completed successfully.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if action completed, False otherwise
        """
        verification = action.get("verification")
        if not verification:
            return True  # No verification required
        
        verification_type = verification.get("type")
        
        if verification_type == "ocr_text":
            expected_text = verification.get("expected_text")
            region = verification.get("region")
            detected_text = self.ui_detector.extract_text_from_region(region)
            return expected_text.lower() in detected_text.lower()
        
        elif verification_type == "template_matching":
            template_path = verification.get("template")
            if template_path:
                return self.ui_detector.find_template(template_path) is not None
        
        return True
    
    def _is_correct_screen_open(self) -> bool:
        """
        Check if the correct screen is open.
        
        Returns:
            bool: True if correct screen, False otherwise
        """
        # This would need to be implemented based on the specific app
        # For now, return True as a placeholder
        return True
    
    def _hotkey(self, action: Dict[str, Any]) -> bool:
        """
        Execute a hotkey combination.
        
        Args:
            action (dict): Action configuration with 'keys' list
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import pyautogui
            keys = action.get("keys", [])
            if not keys:
                print("No keys specified for hotkey action")
                return False
            
            print(f"Executing hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            time.sleep(0.5)  # Allow action to be processed
            return True
        except Exception as e:
            print(f"Error executing hotkey: {e}")
            return False
    
    def _key_press(self, action: Dict[str, Any]) -> bool:
        """
        Press a single key.
        
        Args:
            action (dict): Action configuration with 'key' string
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import pyautogui
            key = action.get("key")
            if not key:
                print("No key specified for key_press action")
                return False
            
            print(f"Pressing key: {key}")
            pyautogui.press(key)
            time.sleep(0.5)  # Allow action to be processed
            return True
        except Exception as e:
            print(f"Error pressing key: {e}")
            return False
    
    def _delete_text(self, action: Dict[str, Any]) -> bool:
        """
        Delete text using various methods.
        
        Args:
            action (dict): Action configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import pyautogui
            method = action.get("method", "select_and_delete")
            text_to_delete = action.get("text_to_delete", "")
            
            if method == "select_and_delete":
                # Select all text and delete
                pyautogui.hotkey("ctrl", "a")
                time.sleep(0.2)
                pyautogui.press("backspace")
            elif method == "select_word_delete":
                # Select specific word and delete
                if text_to_delete:
                    # Find and select the specific text
                    pyautogui.hotkey("ctrl", "f")
                    time.sleep(0.2)
                    pyautogui.typewrite(text_to_delete)
                    time.sleep(0.2)
                    pyautogui.press("enter")
                    time.sleep(0.2)
                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.2)
                    pyautogui.press("backspace")
                    time.sleep(0.2)
                    pyautogui.press("escape")  # Close find dialog
            
            time.sleep(0.5)  # Allow action to be processed
            return True
        except Exception as e:
            print(f"Error deleting text: {e}")
            return False
    
    # Function Dispatcher Implementations
    def _execute_notepad_typing(self) -> bool:
        """Execute notepad basic typing function."""
        try:
            import pyautogui
            print("Executing notepad typing via function dispatcher")
            pyautogui.typewrite("Hello, this is automated typing in Notepad!")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Error in notepad typing function: {e}")
            return False
    
    def _execute_notepad_delete_close(self) -> bool:
        """Execute notepad delete and close function."""
        try:
            import pyautogui
            import pygetwindow as gw
            print("Executing notepad delete and close via function dispatcher")
            
            # First, make sure Notepad is active/focused
            print("Focusing Notepad window...")
            try:
                notepad_windows = gw.getWindowsWithTitle("Notepad")
                if notepad_windows:
                    notepad_windows[0].activate()
                    time.sleep(0.5)
                    print("Notepad window activated")
                else:
                    print("Warning: Notepad window not found")
            except Exception as e:
                print(f"Warning: Could not focus Notepad: {e}")
            
            # Select all text
            print("Selecting all text...")
            pyautogui.hotkey("ctrl", "a")
            time.sleep(1)
            
            # Delete all text
            print("Deleting all text...")
            pyautogui.press("backspace")
            time.sleep(1)
            
            # Focus Notepad again before closing
            print("Re-focusing Notepad before closing...")
            try:
                notepad_windows = gw.getWindowsWithTitle("Notepad")
                if notepad_windows:
                    notepad_windows[0].activate()
                    time.sleep(0.5)
            except Exception as e:
                print(f"Warning: Could not re-focus Notepad: {e}")
            
            # Close Notepad using direct window control
            print("Closing Notepad...")
            
            try:
                # Get Notepad window and close it directly
                notepad_windows = gw.getWindowsWithTitle("Notepad")
                if notepad_windows:
                    notepad_window = notepad_windows[0]
                    print(f"Found Notepad window: {notepad_window.title}")
                    
                    # Close the window directly
                    notepad_window.close()
                    time.sleep(1)
                    
                    # Check if it's actually closed
                    remaining_windows = gw.getWindowsWithTitle("Notepad")
                    if remaining_windows:
                        print("Notepad still open, trying force close...")
                        # Try Alt+F4 as backup
                        notepad_window.activate()
                        time.sleep(0.5)
                        pyautogui.hotkey("alt", "f4")
                        time.sleep(1)
                    else:
                        print("Notepad closed successfully via direct window control")
                else:
                    print("No Notepad window found to close")
            except Exception as e:
                print(f"Error closing Notepad window: {e}")
                # Fallback to Alt+F4
                print("Trying Alt+F4 as fallback...")
                pyautogui.hotkey("alt", "f4")
                time.sleep(1)
            
            print("Close command executed")
            return True
        except Exception as e:
            print(f"Error in notepad delete/close function: {e}")
            return False
    
    def _execute_notepad_advanced_typing(self) -> bool:
        """Execute notepad advanced typing function."""
        try:
            import pyautogui
            print("Executing notepad advanced typing via function dispatcher")
            pyautogui.typewrite("Advanced Notepad Automation\n")
            pyautogui.typewrite("This is a more complex typing task.\n")
            pyautogui.typewrite("Multiple lines with formatting.")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Error in notepad advanced typing function: {e}")
            return False
