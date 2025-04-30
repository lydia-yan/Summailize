from flask import Blueprint, request, jsonify, redirect, url_for
import json
from datetime import datetime
import logging

from app.auth.oauth_handler import get_authorization_url, handle_oauth_callback


from app.storage.db import store_user_settings, get_user_setting, get_overall_summary, get_tokens
from app.scheduler.task_scheduler import update_user_schedule
from app.api.time_utils import utc_to_user_timezone


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
api = Blueprint('api', __name__, url_prefix='/api')


# comment out the OAuth related routes
# user authoerize gmail usage
@api.route("/login")
def login():
    return redirect(get_authorization_url())

@api.route("/oauth2callback")
def oauth2callback():
    user_email = handle_oauth_callback()
    return redirect(url_for('api.connected', email=user_email))

@api.route("/connected")
def connected():
    email = request.args.get("email", "Unknown Email")
    return f"""
    <html>
        <head>
            <title>Connected</title>
            <script>
                window.onload = function() {{
                    alert("✅ Connected successfully as {email}!");
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: "oauth_success",
                            email: "{email}"
                        }}, "*");
                    }}
                    window.close();
                }};
            </script>
        </head>
        <body>
            <p>Connected successfully. You can close this window.</p>
        </body>
    </html>
    """

# summarize
@api.route('/summarize/per', methods=['POST'])
def summarize_email():
    """
    Process a single email content and return summary
    Receive email URL and user settings, return email summary
    """
    try:
        data = request.json
        subject = data.get('subject')
        sender = data.get('sender')
        received_date = data.get('received_date')
        user_id = data.get('user_id')
        
        if not all([subject, sender, received_date, user_id]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # get the email content
        from app.gmail.fetch_emails import _build_query, get_emails_by_query
        gmail_query = _build_query(subject, sender, received_date)
        
        # Fetch emails (only one)
        try:
            emails = get_emails_by_query(gmail_query=gmail_query, user_id=user_id, max_total=1)
            if not emails:
                return jsonify({"error": "No matching email found"}), 404
            
            # generate email summary
            from app.summarizer.summary_checker import run_per_email_summary
            run_per_email_summary(user_id, emails)
            
            # get the summary from the database
            from app.storage.db import get_per_email_summary
            summary = get_per_email_summary(user_id, emails[0]["id"])
            if not summary:
                return jsonify({"error": "Failed to generate summary"}), 500
                
            return jsonify(summary)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/summarize/overall', methods=['POST'])
def periodic_summary():
    """
    Get the generated email summary
    Get the existing summary from the database and convert the timestamp
    """
    try:
        # get user ID
        data = request.json
        user_id = data.get('userId', 'default_user')
        
        # get user settings for timezone conversion
        settings = get_user_setting(user_id)
        user_timezone = settings.get('timeZone', 'UTC+08:00') if settings else 'UTC+08:00'
        
        # get the latest summary from the database
        summary_data = get_overall_summary(user_id)
        if not summary_data:
            return jsonify({'error': 'No summary available'}), 404
        
        # convert the UTC timestamp to the user's timezone
        utc_timestamp = summary_data.get('last_email_timestamp', '')
        local_timestamp = utc_to_user_timezone(utc_timestamp, user_timezone)
        
        # format the response
        summary = {
            'title': 'Periodic Email Summary',
            'dateTime': local_timestamp,
            'items': summary_data.get('overall_summary', [])
        }
        
        return jsonify(summary)
    
    except Exception as e:
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
        
        # save the settings to the database
        store_user_settings(user_id, settings)
        
        # update the user's schedule task
        update_user_schedule(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Settings saved to server',
            'savedSettings': settings
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# test the scheduler
@api.route('/test/trigger/<user_id>', methods=['GET'])
def trigger_task(user_id):
    from app.scheduler.task_scheduler import scheduler
    scheduler._execute_summary_task(user_id)
    return jsonify({"message": f"Triggered summary task for user {user_id}"})

