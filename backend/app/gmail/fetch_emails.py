"""
Grab Gmail messages, clean them,
and return JSON-ready dicts.

Key public helpers
------------------
get_emails_by_query(gmail_query, max_total=50) -> list[dict]
"""


from __future__ import annotations
import base64, html, pathlib, json, os
from typing import Dict, List
from datetime import datetime, timedelta

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from app.storage.db import get_tokens, save_tokens
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from google.auth.transport.requests import Request

MAX_PER_PAGE= 100  # Gmail list() limit

# ─── OAuth helper ────────────────────────────────────────────────────────────
def get_gmail_service(user_id: str):
    """
    Return an authenticated Gmail service for *this* user.
    Tokens are loaded / saved in .tokens/<user_id>.json
    """
    token_data = get_tokens(user_id)
    if not token_data:
        raise Exception("No token data found. User not logged in.")

    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_tokens(user_id, creds.token, creds.refresh_token, creds.expiry.isoformat())

    return build('gmail', 'v1', credentials=creds)

# ─── Internal helpers ────────────────────────────────────────────────────────
def _decode_body(encoded: str) -> str:
    return html.unescape(base64.urlsafe_b64decode(encoded).decode("utf-8", errors="ignore"))

def _extract_headers(headers) -> tuple[str, str, str]:
    subject = sender_name = sender_email = ""
    for h in headers:
        k, v = h["name"], h["value"]
        if k == "Subject":
            subject = v
        elif k == "From":
            if "<" in v:
                n, e = v.split("<")
                sender_name = n.strip().strip('"')
                sender_email = e.replace(">", "").strip()
            else:
                sender_email = v
    return subject, sender_name, sender_email

def _walk_parts(parts, bodies: list[str], atts: list[str]):
    for p in parts:
        if p.get("filename"):
            atts.append(p["filename"])
        if p.get("mimeType") == "text/plain" and "data" in p.get("body", {}):
            bodies.append(p["body"]["data"])
        if "parts" in p:
            _walk_parts(p["parts"], bodies, atts)

def _build_email_dict(service, msg_id: str) -> Dict:
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = msg.get("payload", {})
    subject, s_name, s_email = _extract_headers(payload.get("headers", []))

    bodies, attachments = [], []
    if "parts" in payload:
        _walk_parts(payload["parts"], bodies, attachments)
    elif "body" in payload and "data" in payload["body"]:
        bodies.append(payload["body"]["data"])

    body_plain = _decode_body(bodies[0]) if bodies else ""
    internal_date = msg.get("internalDate", "")

    return {
        "id": msg_id,
        "subject": subject,
        "body": body_plain,
        "attachment_names": attachments,
        "from": {
            "display_name": s_name,
            "email": s_email
        },
        "internalDate": internal_date
    }

def _build_query(subject: str, sender: str, received_date: str) -> str:
    after_date = (datetime.strptime(received_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y/%m/%d")
    before_date = (datetime.strptime(received_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y/%m/%d")
    
    query = f'subject:"{subject}" from:{sender} after:{after_date} before:{before_date}'
    return query

# ─── Public API ──────────────────────────────────────────────────────────────
def get_emails_by_query(gmail_query: str,
                        user_id: str,                      # ▲▲ NEW
                        max_total: int = 50) -> List[Dict]:

    collected: List[Dict] = []
    page_token = None
    service = get_gmail_service(user_id)                   # ▲▲ pass user_id

    try:
        while len(collected) < max_total:
            resp = (service.users()
                          .messages()
                          .list(userId="me",
                                q=gmail_query,
                                 maxResults=min(MAX_PER_PAGE, max_total - len(collected)),
                                pageToken=page_token)
                          .execute())

            for m in resp.get("messages", []):
                collected.append(_build_email_dict(service, m["id"]))

            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except HttpError as e:
        print("⚠️ Gmail API error:", e)

    return collected