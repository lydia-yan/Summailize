import json
import pathlib
from typing import List, Optional
from google.oauth2.credentials import Credentials

TOKEN_DIR = pathlib.Path(".tokens")        # one file per user
TOKEN_DIR.mkdir(exist_ok=True)

def token_path(user_id: str) -> pathlib.Path:
    return TOKEN_DIR / f"{user_id}.json"

def load_tokens(user_id: str, scopes: List[str]) -> Optional[Credentials]:
    fp = token_path(user_id)
    if fp.exists():
        return Credentials.from_authorized_user_file(fp, scopes)
    return None

def save_tokens(user_id: str, creds: Credentials):
    token_path(user_id).write_text(creds.to_json())