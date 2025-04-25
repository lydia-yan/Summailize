from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import redirect, session, request, url_for
import os
from app.storage.db import save_tokens

from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

import json


def build_auth_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('api.oauth2callback', _external=True)
    )

def get_authorization_url():
    flow = build_auth_flow()
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return auth_url

def handle_oauth_callback():
    flow = build_auth_flow()
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    user_email = profile['emailAddress']

    # Save to Firestore
    save_tokens(user_email, creds.token, creds.refresh_token, creds.expiry.isoformat())

    return user_email
