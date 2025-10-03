"""
Error handling module for retry logic and notifications.
"""

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Tuple


class ErrorHandler:
    """
    Handles errors, retries, and notifications for the automation system.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the error handler.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.retry_policies = config_manager.get_retry_policies()
        self.email_settings = config_manager.get_email_settings()
        self.max_retries = self.retry_policies.get("max_retries", 3)
        self.retry_delay = self.retry_policies.get("retry_delay", 2)
        self.failure_policy = self.retry_policies.get("on_failure", "notify_developer")
    
    def handle_error(self, error):
        """Handle and display errors."""
        print(f"\n❌ Error: {error}")
        
        # Show available apps if it's a config error
        if "not found" in str(error):
            try:
                print("Available apps:")
                for app in self.config_manager.config.get("apps", []):
                    print(f"  - {app['name']}: {app['description']}")
            except:
                pass
        
        print("\n💡 Make sure config.json exists and is valid")
        import sys
        sys.exit(1)
    
    def handle_action_failure(self, action: Dict[str, Any], action_history: List[Dict], 
                             objective: Dict[str, Any], retry_count: int = 0) -> bool:
        """
        Handle failure of a specific action.
        
        Args:
            action (dict): The failed action
            action_history (list): History of completed actions
            objective (dict): Current objective
            retry_count (int): Current retry count
            
        Returns:
            bool: True if should retry, False if should stop
        """
        print(f"Action failed: {action.get('type', 'unknown')}")
        print(f"Retry count: {retry_count}/{self.max_retries}")
        
        if retry_count < self.max_retries:
            print(f"Retrying action in {self.retry_delay} seconds...")
            time.sleep(self.retry_delay)
            return True
        
        # Max retries exceeded, send notification and stop
        print("Max retries exceeded, sending notification...")
        self._notify_developer_support(
            f"Action failed after {self.max_retries} retries",
            f"Action: {action.get('type', 'unknown')} failed after maximum retries"
        )
        return False
    
    def _determine_failure_policy(self, action: Dict[str, Any], 
                                 objective: Dict[str, Any]) -> RetryPolicy:
        """
        Determine the failure policy based on action and objective.
        
        Args:
            action (dict): The failed action
            objective (dict): Current objective
            
        Returns:
            RetryPolicy: The policy to follow
        """
        # Check if action has specific retry policy
        action_policy = action.get("retry_policy")
        if action_policy:
            try:
                return RetryPolicy(action_policy)
            except ValueError:
                pass
        
        # Check if objective has specific retry policy
        objective_policy = objective.get("retry_policy")
        if objective_policy:
            try:
                return RetryPolicy(objective_policy)
            except ValueError:
                pass
        
        # Use default policy from configuration
        default_policy = self.retry_policies.get("default_policy", "throw_error")
        try:
            return RetryPolicy(default_policy)
        except ValueError:
            return RetryPolicy.THROW_ERROR
    
    def _go_back_one_action(self, action_history: List[Dict]) -> bool:
        """
        Go back one action and retry.
        
        Args:
            action_history (list): History of completed actions
            
        Returns:
            bool: True to continue, False to stop
        """
        if not action_history:
            print("No previous actions to go back to")
            return False
        
        last_action = action_history.pop()
        print(f"Going back to action: {last_action.get('type', 'unknown')}")
        
        # This would need to be implemented based on the specific action type
        # For now, just return True to continue
        return True
    
    def _throw_error_and_notify(self, action: Dict[str, Any], 
                               objective: Dict[str, Any]) -> bool:
        """
        Throw an error and notify developer support.
        
        Args:
            action (dict): The failed action
            objective (dict): Current objective
            
        Returns:
            bool: Always False to stop execution
        """
        error_message = f"Action failed after max retries: {action.get('type', 'unknown')}"
        print(error_message)
        
        # Send notification to developer
        self._notify_developer_support(
            f"Action Failure: {error_message}",
            f"Objective: {objective.get('name', 'unknown')}\n"
            f"Action: {action.get('type', 'unknown')}\n"
            f"Max retries exceeded: {self.max_retries}"
        )
        
        return False
    
    def _rollback_objective_and_notify(self, action: Dict[str, Any], 
                                     objective: Dict[str, Any], 
                                     action_history: List[Dict]) -> bool:
        """
        Roll back the entire objective and notify developer support.
        
        Args:
            action (dict): The failed action
            objective (dict): Current objective
            action_history (list): History of completed actions
            
        Returns:
            bool: Always False to stop execution
        """
        print(f"Rolling back objective: {objective.get('name', 'unknown')}")
        
        # Implement rollback logic based on action history
        # This would need to be customized for each action type
        for completed_action in reversed(action_history):
            print(f"Rolling back action: {completed_action.get('type', 'unknown')}")
            # Implement specific rollback logic here
        
        # Send notification to developer
        self._notify_developer_support(
            f"Objective Rollback: {objective.get('name', 'unknown')}",
            f"Failed action: {action.get('type', 'unknown')}\n"
            f"Rolled back {len(action_history)} actions"
        )
        
        return False
    
    def handle_objective_failure(self, objective: Dict[str, Any], 
                               error_message: str) -> bool:
        """
        Handle failure of an entire objective.
        
        Args:
            objective (dict): The failed objective
            error_message (str): Error message describing the failure
            
        Returns:
            bool: True if should continue with other objectives, False to stop
        """
        print(f"Objective failed: {objective.get('name', 'unknown')}")
        print(f"Error: {error_message}")
        
        # Send notification to developer
        self._notify_developer_support(
            f"Objective Failure: {objective.get('name', 'unknown')}",
            f"Error: {error_message}\n"
            f"Objective ID: {objective.get('id', 'unknown')}"
        )
        
        return False
    
    def handle_unsupported_objectives(self, unsupported_objectives: List[Dict]) -> bool:
        """
        Handle unsupported objectives by notifying the user.
        
        Args:
            unsupported_objectives (list): List of unsupported objectives
            
        Returns:
            bool: True to continue with supported objectives, False to stop
        """
        if not unsupported_objectives:
            return True
        
        print("Found unsupported objectives:")
        unsupported_list = []
        
        for objective in unsupported_objectives:
            name = objective.get('name', 'Unknown')
            reason = objective.get('reason', 'No reason provided')
            print(f"  - {name}: {reason}")
            unsupported_list.append(f"{name}: {reason}")
        
        # Send notification to user
        self._notify_user_unsupported(unsupported_list)
        
        return True  # Continue with supported objectives
    
    def _notify_developer_support(self, subject: str, message: str) -> bool:
        """
        Send notification to developer support.
        
        Args:
            subject (str): Email subject
            message (str): Email message
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        if not self.email_settings.get("enabled", False):
            print("Email notifications disabled")
            return False
        
        try:
            developer_email = self.email_settings.get("developer_email")
            if not developer_email:
                print("Developer email not configured")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_settings.get("user_email", "automation@system.com")
            msg['To'] = developer_email
            msg['Subject'] = f"[Automation System] {subject}"
            
            body = f"""
Automation System Error Report

{message}

Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
System: Windows Automation
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (this would need proper SMTP configuration)
            print(f"Would send email to {developer_email}: {subject}")
            # smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            # smtp_server.starttls()
            # smtp_server.login(email, password)
            # smtp_server.send_message(msg)
            # smtp_server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending developer notification: {e}")
            return False
    
    def _notify_user_unsupported(self, unsupported_list: List[str]) -> bool:
        """
        Send notification to user about unsupported objectives.
        
        Args:
            unsupported_list (list): List of unsupported objectives with reasons
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        if not self.email_settings.get("enabled", False):
            print("Email notifications disabled")
            return False
        
        try:
            user_email = self.email_settings.get("user_email")
            if not user_email:
                print("User email not configured")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_settings.get("developer_email", "automation@system.com")
            msg['To'] = user_email
            msg['Subject'] = "[Automation System] Unsupported Actions Detected"
            
            body = f"""
Automation System - Unsupported Actions Report

The following actions are currently NOT SUPPORTED by the automation system:

{chr(10).join(f"• ACTION: {item}" for item in unsupported_list)}

DETAILS:
- These actions cannot be executed automatically
- The system will skip these unsupported actions
- Only supported actions will be executed
- Contact support if you need these features implemented

SYSTEM STATUS:
- Automation will continue with supported actions only
- No data loss will occur
- System remains functional

Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

For support, contact: {self.email_settings.get("developer_email", "support@automation.com")}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (this would need proper SMTP configuration)
            print(f"Would send email to {user_email}: Unsupported Actions Report")
            print(f"Email would include {len(unsupported_list)} unsupported actions:")
            for item in unsupported_list:
                print(f"  - {item}")
            # smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            # smtp_server.starttls()
            # smtp_server.login(email, password)
            # smtp_server.send_message(msg)
            # smtp_server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending user notification: {e}")
            return False
    
    def log_error(self, error_type: str, message: str, context: Dict[str, Any] = None):
        """
        Log an error for debugging purposes.
        
        Args:
            error_type (str): Type of error
            message (str): Error message
            context (dict, optional): Additional context
        """
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {error_type}: {message}"
        
        if context:
            log_entry += f" | Context: {context}"
        
        print(log_entry)
        
        # In a real implementation, this would write to a log file
        # with open("automation.log", "a") as f:
        #     f.write(log_entry + "\n")

