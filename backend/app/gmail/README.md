# Gmail Fetcher Module (Fetched from Gmail API)

Fetches raw Gmail messages, cleans them, and returns JSON‑ready dicts you can feed into downstream summarizers.

## What It Does

- **OAuth 2.0** sign‑in for each user (desktop‑app flow)
- Caches/refreshes access + refresh tokens via `app.storage.db`
- Supports Gmail search queries (`newer_than:3d`, `from:bob@corp.com`, …)
- Downloads up to **50** messages per call (configurable)
- Extracts **subject, sender, body (plain‑text), attachment names, internalDate**
- Returns a list of Python dicts, ready for JSON serialisation

## Prerequisites

| Item                                      | Notes                                     |
| ----------------------------------------- | ----------------------------------------- |
| **Python**                                | 3.10 or newer                             |
| **Google Cloud project**                  | Gmail API enabled                         |
| **OAuth 2.0 Client (Desktop)**            | JSON downloaded from Google Cloud Console |
| `google-auth`, `google-api-python-client` | Already in repo’s `requirements.txt`      |


## Enable Gmail API & Store Credentials

1. Open **Google Cloud Console** → select your project (or create one).
2. **APIs & Services → Library** → enable **Gmail API**.
3. **OAuth consent screen** → External/Internal → add your test Gmail accounts.
4. **Credentials → Create credentials → OAuth client ID** → *Desktop app*.
5. Download the JSON → rename it to **`client_secret_.json`**.


### After you getting the credentials
Put **`client_secret_.json`** into the  **`backend/.env`** :
```ini
GOOGLE_CLIENT_SECRET_PATH=credentials/client_secret_.json
```
**Keep it in the `.env` secret & git‑ignored.** If it’s deleted or revoked, the user will be asked to sign in again.

## Email Dict Schema
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
  "internalDate": "1713412345000"
}
```

## Quick Start
Once a user completed OAuth (tokens are stored in Firestore) in frontend, you can query their Gmail using:
```python
emails = get_emails_by_query(
    gmail_query="newer_than:3d -category:promotions",
    user_id="<your-firebase-uid or any unique user key>",
    max_total=20,
)

print(len(emails))
print(emails[0]["subject"], emails[0]["internalDate"])
```
✅ This is useful for quickly verifying Gmail access and Firestore token setup during development.


## Token Storage Contract

The Gmail integration relies on token management handled by helper functions in `app.storage.db`. These functions allow the system to persist and retrieve OAuth tokens for each user.



| Function                                            | Purpose                                                      |
| --------------------------------------------------- | ------------------------------------------------------------ |
| `get_tokens(user_id)`                               | Return `{access_token, refresh_token, expiry}` dict or `None` |
| `save_tokens(user_id, access, refresh, expiry_iso)` | Persist new tokens                                           |

These helpers abstract away the token persistence layer (e.g. Firebase, Firestore), enabling flexibility across environments.


## Gmail Functions
These core functions in the Gmail module handle email retrieval and query construction:



| Function                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `get_emails_by_query(q: str, user_id: str, max_total: int = 50)` | Search Gmail and return a list of message dicts              |
| `_build_query(subject, sender, received_date)`               | Helper that crafts an exact match query (subject + sender) – rarely needed externally |
