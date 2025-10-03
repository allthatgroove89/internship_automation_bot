"""
Configuration management module for handling JSON configuration files.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple


class ConfigManager:
    """
    Manages application configuration from JSON files.
    """
    
    def __init__(self, config_file: str = "config/config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config_file = config_file
        self.config = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            dict: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return self.config
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file: {e}")
    
    def get_app_config(self, app_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific application.
        
        Args:
            app_name (str): Name of the application
            
        Returns:
            dict: Application configuration
            
        Raises:
            ValueError: If app not found in config
        """
        if not app_name:
            raise ValueError("App name cannot be empty")
        
        apps = self.config.get("apps", [])
        if not apps:
            raise ValueError("No apps configured in config file")
        
        for app in apps:
            if app.get("name") == app_name:
                # Validate that the app config has required fields
                required_fields = ["name", "path", "description"]
                missing_fields = [field for field in required_fields if field not in app]
                if missing_fields:
                    raise ValueError(f"App '{app_name}' configuration is incomplete. Missing fields: {missing_fields}")
                return app
        
        available_apps = [app.get("name", "Unknown") for app in apps]
        raise ValueError(f"App '{app_name}' not found in config. Available apps: {available_apps}")
    
    def get_default_app(self) -> str:
        """
        Get the default application name.
        
        Returns:
            str: Default application name
        """
        return self.config.get("default_app", "Notepad")
    
    def get_objectives(self, objective_ids: List[str] = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Get objectives from instructions file, separating supported and unsupported.
        
        Args:
            objective_ids (list, optional): Specific objective IDs to get
            
        Returns:
            tuple: (supported_objectives, unsupported_objectives)
        """
        # Load objectives from separate instructions file
        instructions_file = self.config.get("instructions_file", "config/instructions.json")
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = json.load(f)
            objectives = instructions.get("objectives", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading instructions file: {e}")
            objectives = []
        
        if objective_ids:
            objectives = [obj for obj in objectives if obj["id"] in objective_ids]
        
        supported = []
        unsupported = []
        
        for objective in objectives:
            if objective.get("supported", False):
                supported.append(objective)
            else:
                unsupported.append(objective)
        
        return supported, unsupported
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """
        Get workflow templates from instructions file.
        
        Returns:
            list: List of workflow templates
        """
        instructions_file = self.config.get("instructions_file", "config/instructions.json")
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = json.load(f)
            return instructions.get("workflow_templates", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading workflow templates: {e}")
            return []
    
    def get_retry_policies_from_instructions(self) -> Dict[str, Any]:
        """
        Get retry policies from instructions file.
        
        Returns:
            dict: Retry policies configuration
        """
        instructions_file = self.config.get("instructions_file", "config/instructions.json")
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = json.load(f)
            return instructions.get("retry_policies", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading retry policies: {e}")
            return {}
    
    def get_verification_settings(self) -> Dict[str, Any]:
        """
        Get verification settings from instructions file.
        
        Returns:
            dict: Verification settings
        """
        instructions_file = self.config.get("instructions_file", "config/instructions.json")
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = json.load(f)
            return instructions.get("verification_settings", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading verification settings: {e}")
            return {}
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get application settings.
        
        Returns:
            dict: Settings configuration
        """
        return self.config.get("settings", {})
    
    def get_retry_policies(self) -> Dict[str, Any]:
        """
        Get retry policies from settings.
        
        Returns:
            dict: Retry policies configuration
        """
        settings = self.get_settings()
        return settings.get("retry_policies", {})
    
    def get_email_settings(self) -> Dict[str, Any]:
        """
        Get email notification settings.
        
        Returns:
            dict: Email settings configuration
        """
        settings = self.get_settings()
        return settings.get("email_notifications", {})
    
    def is_ocr_enabled(self) -> bool:
        """
        Check if OCR is enabled in settings.
        
        Returns:
            bool: True if OCR is enabled, False otherwise
        """
        settings = self.get_settings()
        return settings.get("enable_ocr", False)
    
    def get_screenshot_path(self) -> str:
        """
        Get the screenshot path from settings.
        
        Returns:
            str: Screenshot file path
        """
        settings = self.get_settings()
        return settings.get("screenshot_path", "screen.png")
    
    def get_window_position(self) -> Dict[str, int]:
        """
        Get window position settings.
        
        Returns:
            dict: Window position (x, y coordinates)
        """
        settings = self.get_settings()
        return settings.get("window_position", {"x": 0, "y": 0})
    
    def get_app_verification_templates(self, app_name: str) -> List[Dict[str, Any]]:
        """
        Get verification templates for a specific app.
        
        Args:
            app_name (str): Name of the application
            
        Returns:
            list: List of verification templates
        """
        app_config = self.get_app_config(app_name)
        return app_config.get("verification_templates", [])
    
    def get_app_max_retries(self, app_name: str) -> int:
        """
        Get maximum retries for a specific app.
        
        Args:
            app_name (str): Name of the application
            
        Returns:
            int: Maximum number of retries
        """
        app_config = self.get_app_config(app_name)
        return app_config.get("max_retries", 3)
    
    def save_config(self, new_config: Dict[str, Any] = None) -> bool:
        """
        Save configuration to JSON file.
        
        Args:
            new_config (dict, optional): New configuration to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if new_config:
                self.config = new_config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def add_app(self, app_config: Dict[str, Any]) -> bool:
        """
        Add a new application to the configuration.
        
        Args:
            app_config (dict): Application configuration
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            if "apps" not in self.config:
                self.config["apps"] = []
            
            self.config["apps"].append(app_config)
            return self.save_config()
        except Exception as e:
            print(f"Error adding app: {e}")
            return False
    
    def add_objective(self, objective_config: Dict[str, Any]) -> bool:
        """
        Add a new objective to the configuration.
        
        Args:
            objective_config (dict): Objective configuration
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            if "objectives" not in self.config:
                self.config["objectives"] = []
            
            self.config["objectives"].append(objective_config)
            return self.save_config()
        except Exception as e:
            print(f"Error adding objective: {e}")
            return False
    
    def get_verification_templates(self, app_name: str) -> List[str]:
        """
        Get verification templates for a specific app.
        
        Args:
            app_name (str): Name of the application
            
        Returns:
            list: List of template file paths for verification
        """
        try:
            app_config = self.get_app_config(app_name)
            if not app_config:
                return []
            
            return app_config.get("verification_templates", [])
        except Exception as e:
            print(f"Error getting verification templates: {e}")
            return []
