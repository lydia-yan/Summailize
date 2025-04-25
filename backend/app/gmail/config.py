import os, json
from dotenv import load_dotenv

# Load values from .env file
load_dotenv()

CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_PATH")


with open(CLIENT_SECRETS_FILE) as f:
    data = json.load(f)
    GOOGLE_CLIENT_ID = data["installed"]["client_id"]
    GOOGLE_CLIENT_SECRET = data["installed"]["client_secret"]
