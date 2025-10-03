"""
Enhanced App Automation module using separated components.
"""

import time
from config_manager import ConfigManager
from window_manager import WindowManager
from ui_detection import UIDetector
from error_handler import ErrorHandler
from workflow import WorkflowExecutor


class SimpleAppAutomation:
    """
    Enhanced automation class using modular components.
    
    This class orchestrates the automation process using separate modules
    for configuration, window management, UI detection, and error handling.
    """
    
    def __init__(self, app_name: str, config_manager: ConfigManager = None):
        """
        Initialize the automation object.
        
        Args:
            app_name (str): Name of the application
            config_manager (ConfigManager, optional): Configuration manager instance
        """
        self.app_name = app_name
        self.config_manager = config_manager or ConfigManager()
        self.window_manager = WindowManager(self.config_manager)
        self.ui_detector = UIDetector(self.config_manager)
        self.error_handler = ErrorHandler(self.config_manager)
        self.workflow_executor = WorkflowExecutor(self.config_manager)
        
        # Set up the app in window manager
        if not self.window_manager.set_app(app_name):
            raise ValueError(f"Failed to configure app: {app_name}")

    def run(self, objective_ids: list = None):
        """
        Run the complete automation sequence.
        
        Args:
            objective_ids (list, optional): Specific objective IDs to execute
        """
        print(f"Starting enhanced automation for {self.app_name}...")
        
        try:
            # Step 1: Prepare the application
            if not self.prepare_application():
                print("Application preparation failed")
                return False
            
            # Step 2 & 3: Execute objectives and handle errors
            if not self.execute_objectives(objective_ids):
                print("Objective execution failed")
                return False
            
            # Clean up screenshots after automation is complete
            print("=== Cleaning up temporary files ===")
            self.ui_detector.cleanup_screenshots()
            
            print("Enhanced automation completed successfully!")
            return True
            
        except Exception as e:
            print(f"Unexpected error in automation: {e}")
            self.error_handler.log_error("AUTOMATION_ERROR", str(e))
            return False

    def prepare_application(self, max_retries: int = 3) -> bool:
        """
        Prepare the application - ensure single instance, maximize and focus.
        
        Args:
            max_retries (int): Maximum number of retries for each step
        
        Returns:
            bool: True if application is prepared successfully, False otherwise
        """
        print(f"=== Step 1: Preparing application {self.app_name} ===")
        
        # Use the window manager's complete preparation method
        return self.window_manager.prepare_application(max_retries)


    def execute_objectives(self, objective_ids: list = None) -> bool:
        """
        Execute objectives following the detailed instructions.
        
        Args:
            objective_ids (list, optional): Specific objective IDs to execute
            
        Returns:
            bool: True if all objectives executed successfully, False otherwise
        """
        print("=== Step 2: Preparing objectives ===")
        
        # Parse objectives and identify supported/unsupported
        supported_objectives, unsupported_objectives = self.workflow_executor.parse_objectives(objective_ids)
        
        # Handle unsupported objectives
        if unsupported_objectives:
            print("Found unsupported objectives:")
            for obj in unsupported_objectives:
                print(f"  - {obj['name']}: {obj.get('reason', 'No reason provided')}")
            
            if not self.error_handler.handle_unsupported_objectives(unsupported_objectives):
                return False
        
        if not supported_objectives:
            print("No supported objectives to execute")
            return True
        
        print(f"Executing {len(supported_objectives)} supported objectives")
        
        # Execute each supported objective
        for objective in supported_objectives:
            print(f"\n=== Executing objective: {objective['name']} ===")
            
            if not self.workflow_executor.execute_objective(objective):
                print(f"Objective '{objective['name']}' failed")
                if not self.error_handler.handle_objective_failure(
                    objective, "Objective execution failed"
                ):
                    return False
            else:
                print(f"Objective '{objective['name']}' completed successfully")
        
        return True
    # for debugging
    def get_window_info(self) -> dict:
        """
        Get information about the current window.
        
        Returns:
            dict: Window information
        """
        return self.window_manager.get_window_info()

    def take_screenshot(self, save_path: str = None) -> str:
        """
        Take a screenshot of the current screen.
        
        Args:
            save_path (str, optional): Path to save the screenshot
            
        Returns:
            str: Path to the saved screenshot
        """
        return self.ui_detector.take_screenshot(save_path)

    def close_application(self) -> bool:
        """
        Close the current application.
        
        Returns:
            bool: True if closed successfully, False otherwise
        """
        return self.window_manager.close_window()
