#!/usr/bin/env python3
"""
Simple main entry point for the automation system.
Clean, readable version with clear flow.
"""

import sys
import os
import json
import psutil
from config_manager import ConfigManager
from automation import SimpleAppAutomation
from error_handler import ErrorHandler


def main():
    """Main function"""
    print("Automation System Starting...")
    print("=" * 50)
    
    try:
        # Step 1: Load configuration
        print("Loading configuration...")
        config_manager = ConfigManager()
        print("Configuration loaded successfully")
        
        # Step 2: Get app name (use default or from command line)
        if len(sys.argv) > 1:
            app_name = sys.argv[1]
            print(f"Using specified app: {app_name}")
        else:
            app_name = config_manager.get_default_app()
            print(f"Using default app: {app_name}")
        
        # Verify app is running
        if not is_app_running_standalone(app_name):
            print(f"Warning: {app_name} is not currently running")
            print("The automation will attempt to launch it if needed.")
        
        # Step 3: Get app settings
        print(f"Getting configuration for {app_name}...")
        app_config = config_manager.get_app_config(app_name)
        
        if not app_config:
            available_apps = [app["name"] for app in config_manager.config.get("apps", [])]
            raise ValueError(f"App '{app_name}' not found. Available: {available_apps}")
        
        print(f"App: {app_config['name']}")
        print(f"Description: {app_config['description']}")
        
        # Step 4: Run automation
        app_name = app_config['name']
        
        # Get objective IDs if specified
        objective_ids = None
        if len(sys.argv) > 2:
            objective_ids = sys.argv[2].split(',')
            print(f"Specific objectives: {objective_ids}")
        
        print(f"\nStandard Automation")
        success = run_standard_automation(app_name, objective_ids)
        
        # Step 5: Clean up and finish
        finish_automation(success)
        
    except Exception as e:
        error_handler = ErrorHandler(ConfigManager())
        error_handler.handle_error(e)


# def run_automation(app_config):
#     """Run the automation process."""
#     app_name = app_config['name']
#     
#     # Get objective IDs if specified
#     objective_ids = None
#     if len(sys.argv) > 2:
#         objective_ids = sys.argv[2].split(',')
#         print(f"🎯 Specific objectives: {objective_ids}")
#     
#     # Choose automation mode
#     use_template_mode = app_config.get("use_template_mode", False)
#     
#     if use_template_mode:
#         print(f"\nTemplate-Based Automation")
#         return run_template_automation(app_name, objective_ids)
#     else:
#         print(f"\nStandard Automation")
#         return run_standard_automation(app_name, objective_ids)


def run_standard_automation(app_name, objective_ids):
    """Run standard automation mode."""
    try:
        config_manager = ConfigManager()
        automation = SimpleAppAutomation(app_name, config_manager)
        return automation.run(objective_ids)
    except Exception as e:
        print(f"Standard automation failed: {e}")
        return False


# def run_template_automation(app_name, objective_ids):
#     """Run template-based automation mode."""
#     print(f"Template automation not available - using standard automation instead")
#     return run_standard_automation(app_name, objective_ids)


# def load_workflow_from_json(app_name, objective_ids):
#     """Load workflow from JSON objectives (not workflow_templates)."""
#     try:
#         # Load instructions from JSON
#         with open("config/instructions.json", 'r', encoding='utf-8') as f:
#             instructions = json.load(f)
#         
#         # Get objectives for the app
#         objectives = instructions.get("objectives", [])
#         app_objectives = [obj for obj in objectives if obj.get("app") == app_name]
#         
#         # Filter by objective_ids if specified
#         if objective_ids:
#             app_objectives = [obj for obj in app_objectives if obj.get("id") in objective_ids]
#         
#         # Get supported objectives only
#         supported_objectives = [obj for obj in app_objectives if obj.get("supported", False)]
#         
#         if not supported_objectives:
#             print(f"No supported objectives found for {app_name}")
#             print(f"Available objectives for {app_name}:")
#             for obj in app_objectives:
#                 status = "supported" if obj.get("supported", False) else "unsupported"
#                 reason = obj.get("reason", "")
#                 print(f"  - {obj.get('id', 'unknown')}: {status} {reason}")
#             return {"app": app_name, "actions": []}
#         
#         # Build workflow from objectives
#         all_actions = []
#         for objective in supported_objectives:
#             actions = objective.get("actions", [])
#             all_actions.extend(actions)
#             print(f"Added {len(actions)} actions from objective: {objective.get('name', 'unknown')}")
#         
#         workflow = {
#             "app": app_name,
#             "actions": all_actions
#         }
#         
#         print(f"Built workflow with {len(all_actions)} total actions from {len(supported_objectives)} objectives")
#         return workflow
#         
#     except Exception as e:
#         print(f"Error loading workflow from JSON: {e}")
#         print("Using empty workflow as fallback")
#         return {"app": app_name, "actions": []}


def finish_automation(success):
    """Finish automation and show results."""
    print("\n" + "=" * 50)
    
    if success:
        print("Automation completed successfully!")
    else:
        print("Automation completed with errors!")
        sys.exit(1)
    
    print("=" * 50)


def is_app_running_standalone(app_name):
    """Check if an app is currently running (standalone version for main.py)."""
    try:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == app_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        print(f"Error checking if {app_name} is running: {e}")
        return False




if __name__ == "__main__":
    main()
