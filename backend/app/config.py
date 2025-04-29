import os, json
from dotenv import load_dotenv

# Load values from .env file
# Load variables from .env
load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_PATH")


with open(CLIENT_SECRETS_FILE) as f:
    data = json.load(f)
    GOOGLE_CLIENT_ID = data["installed"]["client_id"]
    GOOGLE_CLIENT_SECRET = data["installed"]["client_secret"]

