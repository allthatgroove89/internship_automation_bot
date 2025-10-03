#!/usr/bin/env python3
"""
Simple email test script
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test if email configuration is set up correctly."""
    print("🔍 Testing Email Configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your email credentials")
        return False
    
    # Check environment variables
    email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', '587')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_username)
    to_email = os.getenv('TO_EMAIL', 'saul.vera787@gmail.com')
    
    print(f"📧 Email Enabled: {email_enabled}")
    print(f"📧 SMTP Server: {smtp_server}")
    print(f"📧 SMTP Port: {smtp_port}")
    print(f"📧 Username: {smtp_username}")
    print(f"📧 Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    print(f"📧 From Email: {from_email}")
    print(f"📧 To Email: {to_email}")
    
    # Validate required fields
    missing_fields = []
    if not smtp_username:
        missing_fields.append("SMTP_USERNAME")
    if not smtp_password:
        missing_fields.append("SMTP_PASSWORD")
    
    if missing_fields:
        print(f"\n❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    if not email_enabled:
        print(f"\n❌ Email is disabled (EMAIL_ENABLED=false)")
        return False
    
    print(f"\n✅ Email configuration looks good!")
    return True

def send_test_email():
    """Send a test email using the automation system."""
    print("\n📧 Sending Test Email...")
    print("=" * 50)
    
    try:
        from single_script_automation import SingleScriptAutomation
        
        # Create automation instance (we don't need to launch app for email test)
        automation = SingleScriptAutomation("TestApp", "notepad.exe")
        
        # Test email
        subject = "🧪 Test Email from Automation System"
        message = """
Hello Saul!

This is a test email from your automation system.

If you receive this email, the email configuration is working correctly! 🎉

Test Details:
- System: Single Script Automation
- Purpose: Email functionality test
- Status: SUCCESS ✅
- Time: """ + str(__import__('datetime').datetime.now())

        result = automation.send_email_notification(subject, message)
        
        if result:
            print("✅ Email sent successfully!")
            print("📧 Check your inbox for the test email")
            print("📧 Look for subject: '🧪 Test Email from Automation System'")
        else:
            print("❌ Email sending failed")
            
        return result
        
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Email Testing Script")
    print("=" * 50)
    
    # Test 1: Configuration
    if test_email_config():
        print("\n" + "=" * 50)
        
        # Test 2: Send email
        send_test_email()
    
    print("\n" + "=" * 50)
    print("🏁 Email testing completed!")
