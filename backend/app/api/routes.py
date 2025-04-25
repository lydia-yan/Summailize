from flask import Blueprint, request, jsonify, redirect
import json
from datetime import datetime
import logging
from app.auth.oauth_handler import get_authorization_url, handle_oauth_callback


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Simple in-memory data storage for user settings
# In a real application, a database should be used
user_settings = {}

# user authoerize gmail usage
@api.route("/login")
def login():
    return redirect(get_authorization_url())

@api.route("/oauth2callback")
def oauth2callback():
    user_email = handle_oauth_callback()
    return redirect(f"/connected?email={user_email}")

@api.route("/get-emails")
def get_emails():
    user_email = request.args.get("user_id")
    emails = list_emails(user_email) #replace the function from fetch_email.py
    return jsonify(emails) 

# summarize
@api.route('/summarize/per', methods=['POST'])
def summarize_email():
    """
    Process a single email content and return summary
    Receive email URL and user settings, return email summary
    """
    try:
        data = request.json
        email_url = data.get('emailUrl')
        settings = data.get('userSettings', {})
        
        logger.info(f"Received email summary request, URL: {email_url}")
        
        # Here should add actual email processing logic
        # For example: call NLP service to analyze email content
        
        # Example response data
        # In actual application, this part should be generated based on actual email content
        email_id = email_url.split('/')[-1] if email_url else 'unknown'
        
        summary = {
            'subject': f'Email Subject: {email_id}',
            'sender': 'sender@example.com',
            'summary': 'This email discusses the latest project progress and upcoming deadlines. The author mentions several key points: 1) UI upgrades need to be completed next week; 2) New feature testing will begin this Friday; 3) A team meeting needs to be scheduled to discuss implementation details.'
        }
        
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/summarize/overall', methods=['POST'])
def periodic_summary():
    """
    Generate periodic email summary
    Generate comprehensive summary report based on user settings
    """
    try:
        # In actual application, here should get recent emails from database and analyze them
        
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        # Example summary data
        # In actual application, this part should be generated based on actual email data
        summary = {
            'title': 'Periodic Email Summary',
            'dateTime': current_time,
            'items': [
                {
                    'id': 'summary1',
                    'category': 'Recruitment Information',
                    'content': 'This week, you received 15 recruitment-related emails, mainly focusing on software engineering, data analysis and product manager positions. Five of them are from large technology companies.'
                },
                {
                    'id': 'summary2',
                    'category': 'Subscription Newsletter',
                    'content': 'Received 3 subscription newsletters, including the latest AI development dynamics and React framework update information.'
                },
                {
                    'id': 'summary3',
                    'category': 'Important Emails',
                    'content': 'Received 2 important emails, including a project collaboration invitation and a meeting arrangement confirmation.'
                }
            ]
        }
        
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error generating periodic summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/settings', methods=['POST'])
def save_settings():
    """
    Save user settings
    Receive and save user preference settings
    """
    try:
        settings = request.json
        user_id = settings.get('userId', 'default_user')  # In a real application, should get user ID from authentication
        
        logger.info(f"Saving user settings, User ID: {user_id}")
        
        # In a real application, should save settings to database
        user_settings[user_id] = settings
        
        return jsonify({
            'success': True,
            'message': 'Settings saved to server',
            'savedSettings': settings
        })
    
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return jsonify({'error': str(e)}), 500