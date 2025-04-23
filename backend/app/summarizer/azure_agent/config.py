import os
from dotenv import load_dotenv

# Load values from .env file
load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
