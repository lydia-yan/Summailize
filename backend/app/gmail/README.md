# Gmail Fetcher Module (`app/gmail/fetch_emails.py`)

Fetches raw Gmail messages, cleans them, and returns JSON‑ready dicts you can feed into downstream summarizers.

---

## What It Does

- **OAuth 2.0** sign‑in for each user (desktop‑app flow)
- Caches/refreshes access + refresh tokens via `app.storage.db`
- Supports Gmail search queries (`newer_than:3d`, `from:bob@corp.com`, …)
- Downloads up to **50** messages per call (configurable)
- Extracts **subject, sender, body (plain‑text), attachment names, internalDate**
- Returns a list of Python dicts, ready for JSON serialisation

---

## Prerequisites

| Item                                      | Notes                                     |
| ----------------------------------------- | ----------------------------------------- |
| **Python**                                | 3.10 or newer                             |
| **Google Cloud project**                  | Gmail API enabled                         |
| **OAuth 2.0 Client (Desktop)**            | JSON downloaded from Google Cloud Console |
| `google-auth`, `google-api-python-client` | Already in repo’s `requirements.txt`      |

---

## 1. Enable Gmail API & Download Credentials

1. Open **Google Cloud Console** → select your project (or create one).
2. **APIs & Services → Library** → enable **Gmail API**.
3. **OAuth consent screen** → External/Internal → add your test Gmail accounts.
4. **Credentials → Create credentials → OAuth client ID** → *Desktop app*.
5. Download the JSON → rename it to something memorable, e.g. **`client_secret*.json`**.
6. Place it in **`/backend/app/gmail`**.

---

## 2. Environment Variables

Create / update **`.env`** in **`/backend/app/gmail`**:

```ini
# Path relative to backend/
CLIENT_SECRET_FILE=client_secret*.json

# Where you store service‑account creds if you use Firestore for tokens
TOKEN_FILE=token.json
```

---

## 3. Quick Start

```python
from app.gmail.fetch_emails import get_emails_by_query

# 1. The user must have finished OAuth once; tokens are now stored in Firestore
emails = get_emails_by_query(
    gmail_query="newer_than:3d -category:promotions",
    user_id="<firebase‑uid or any string you use as user key>",
    max_total=20,
)

print(len(emails))
print(emails[0]["subject"], emails[0]["internalDate"])
```

### Email Dict Schema

```json
{
  "id": "186e8d…",
  "subject": "Weekly report",
  "body": "Plain‑text body …",
  "attachment_names": ["report.pdf"],
  "from": {
    "display_name": "Alice Chen",
    "email": "alice@example.com"
  },
  "internalDate": "1713412345000"  // unix ms since epoch
}
```

---

## 4. Token Storage Contract

The module calls two helpers from **`app.storage.db`**:

| Function                                            | Purpose                                                      |
| --------------------------------------------------- | ------------------------------------------------------------ |
| `get_tokens(user_id)`                               | Return `{access_token, refresh_token, expiry}` dict or `None` |
| `save_tokens(user_id, access, refresh, expiry_iso)` | Persist new tokens                                           |

Feel free to swap in your own storage layer (SQLite, Redis, etc.) as long as you keep the same signature.

---

## 5. Public API Reference

| Function                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `get_emails_by_query(q: str, user_id: str, max_total: int = 50)` | Search Gmail and return a list of message dicts              |
| `_build_query(subject, sender, received_date)`               | Helper that crafts an exact match query (subject + sender) – rarely needed externally |



---

## 6. Sample Credential Files

### 6.1 client_secret*.json

A minimal **desktop‑app** OAuth client downloaded from Google Cloud:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your‑project‑id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "http://localhost"
    ]
  }
}
```

Place this JSON in `/backend/app/gmail` and point `CLIENT_SECRET_FILE` to it.

### 6.2 `token.json` (auto‑generated)

Once a user completes the OAuth flow, the fetcher writes / refreshes a token file next to `client_secret*.json`:

```json
{
  "token": "ya29.a0…",
  "refresh_token": "1//0g…",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.readonly"
  ],
  "expiry": "2025-04-26T03:19:53.659069Z"
}
```

> **Keep it secret & git‑ignored.** If it’s deleted or revoked, the user will be asked to sign in again.
