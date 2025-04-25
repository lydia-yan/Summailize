"""
Grab Gmail messages, clean them, convert times,
and return JSON-ready dicts.

Key public helpers
------------------
get_single_email(email_id, user_tz="UTC+08:00")   -> dict
get_emails_by_query(query, user_tz, max_total=50) -> list[dict]
"""

from __future__ import annotations

import base64, html, pathlib, json
from typing import Dict, List

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors    import HttpError
from google.oauth2.credentials import Credentials

from time_utils import internal_ms_to_tz_iso, internal_ms_to_utc_iso
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

load_dotenv()

SCOPES           = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_SECRET_FP = os.getenv("CLIENT_SECRET_FILE", "client_secret.json")
TOKEN_FP         = os.getenv("TOKEN_FILE", "token.json")
MAX_PER_PAGE     = 100                   # Gmail list() limit

"""
OAuth helper 
Uses your local client_secret_*.json file to perform Google OAuth2 login Automatically saves a token.json to avoid repeated logins
"""

def get_gmail_service():
    """Return an authenticated Gmail service object (re-uses token.json when possible)."""
    creds = None
    token_path = pathlib.Path(TOKEN_FP)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FP, SCOPES)

    if creds is None or not creds.valid:
        flow  = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FP, SCOPES)
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)

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
                sender_name  = n.strip().strip('"')
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

def _build_email_dict(service, msg_id: str, user_tz: str) -> Dict:
    """Low-level builder that returns cleaned email dict (no summary)."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = msg.get("payload", {})
    subject, s_name, s_email = _extract_headers(payload.get("headers", []))

    bodies, attachments = [], []
    if "parts" in payload:
        _walk_parts(payload["parts"], bodies, attachments)
    elif "body" in payload and "data" in payload["body"]:
        bodies.append(payload["body"]["data"])

    body_plain = _decode_body(bodies[0]) if bodies else ""
    internal   = msg.get("internalDate", "")

    return {
        "id"              : msg_id,
        "subject"         : subject,
        "body"            : body_plain,
        "attachment_names": attachments,
        "from"            : {"display_name": s_name, "email": s_email},
        "internalDate"    : internal,
        "received_at"     : internal_ms_to_tz_iso(internal, user_tz),
        "received_at_utc" : internal_ms_to_utc_iso(internal),
    }

# ─── Public helpers 
# Fetches one email by its email_id, extracts relevant fields, and returns a structured dictionary

def get_single_email(email_id: str, user_tz: str = "UTC+08:00") -> Dict:
    """Fetch and clean one Gmail email by its message ID."""
    service = get_gmail_service()
    return _build_email_dict(service, email_id, user_tz)

# Uses Gmail search queries (like newer_than:3d, after:2025/04/01) to fetch a batch of emails.
def get_emails_by_query(
    gmail_query: str,
    user_tz: str,
    max_total: int = 50,
) -> List[Dict]:
    """
    Fetch & clean all emails matching a Gmail search query.
    Example queries:
        'after:2025/04/20 before:2025/04/22'
        'newer_than:7d'
    """
    collected: List[Dict] = []
    page_token = None
    service = get_gmail_service()

    try:
        while len(collected) < max_total:
            resp = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q=gmail_query,
                    maxResults=min(MAX_PER_PAGE, max_total - len(collected)),
                    pageToken=page_token,
                )
                .execute()
            )

            for m in resp.get("messages", []):
                collected.append(_build_email_dict(service, m["id"], user_tz))

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    except HttpError as e:
        print("⚠️ Gmail API error:", e)

    return collected


def email_id_from_url(url: str) -> str | None:
    """
    Gmail message URLs look like
    https://mail.google.com/mail/u/0/#inbox/<MSG_ID>
    or .../0/#all/<thread-id>/<MSG-ID>
    We return the last path segment as the message ID.
    """
    if not url:           # guard
        return None
    return url.rstrip("/").split("/")[-1]

# ─── CLI test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1) test single email (replace with a real message ID)
    # single = get_single_email("YOUR_MESSAGE_ID", "UTC+08:00")
    # print(json.dumps(single, ensure_ascii=False, indent=2))

    # 2) test batch (recent 3 days)
    batch = get_emails_by_query("newer_than:3d", "UTC+08:00", 10)
    print(f"Fetched {len(batch)} emails.")
    with open("emails.json", "w", encoding="utf-8") as fp:
        json.dump(batch, fp, ensure_ascii=False, indent=2)
    print("Saved → emails.json")