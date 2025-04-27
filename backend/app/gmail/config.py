import os, json
from dotenv import load_dotenv

# Load variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(dotenv_path)

# fix GOOGLE_APPLICATION_CREDENTIALS to be absoulute path
if "GOOGLE_CLIENT_SECRET_PATH" in os.environ:
    google_cred = os.environ["GOOGLE_CLIENT_SECRET_PATH"]
    if not os.path.isabs(google_cred):
        abs_cred = os.path.abspath(os.path.join(os.path.dirname(dotenv_path), google_cred))
        os.environ["GOOGLE_CLIENT_SECRET_PATH"] = abs_cred


CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_PATH")


with open(CLIENT_SECRETS_FILE) as f:
    data = json.load(f)
    GOOGLE_CLIENT_ID = data["installed"]["client_id"]
    GOOGLE_CLIENT_SECRET = data["installed"]["client_secret"]
