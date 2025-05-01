# Summarization Agent (Backend) 

## Features
- Connects to Gmail API to fetch recent user emails
- Uses Azure Language AI and OpenAI to generate:
  - Per-email summaries
  - Overall summaries (grouped by category)
- Automatically categorizes emails (e.g., Event, Reminder, Security)
- Supports scheduled summarization per user
- Stores summaries and settings in Firestore (Google Cloud)
- Exposes REST API for frontend or extension usage

## Setup Instructions
### 1. Prerequisites
- Python 3.10+
- Firebase project + service account key (Firestore)
- Azure OpenAI endpoint + API key
- Gmail API client credentials (User doesn't need)

### 2. Installation
```bash
# Clone the repo
git clone https://github.com/lydia-yan/summailize.git
cd summailize

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```
### 3. Environment Variables
Create a `.env` file in the `backend` folder:
```python
AZURE_LANGUAGE_KEY=your-azure-language-key
AZURE_LANGUAGE_ENDPOINT=...
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=...
GOOGLE_APPLICATION_CREDENTIALS=credentials/firebase_key.json
GOOGLE_CLIENT_SECRET_PATH=credentials/client_secret_.json
FLASK_SECRET_KEY=any-text-here
```

Put the below files in `crededntials` folder in the `backend` folder:
- `client_secret_.json`: Gmail API Key
- `firebase_key.json`: Firebase API Key

You can find how to create the above keys in there files:
- [Azure OpenAI and Language keys](./app/summarizer/azure_agent/README.md)
- [FireBase Database Key](./app/storage/README.md)
- [Gmail API Key](./app/gmail/README.md)

## How to Run
1. Run the Backend API Server (FlaskAPI)
```python
cd backend
python main.py
```
This will start the Flask API server to handle email fetching, summarization, and data storage.


2. Build and Run the Frontend (Chrome Extension)
In another terminal window:
```bash
nvm install 
nvm run build
```
This will generate a `dist` folder containing the built extension files.

- Go to `Chrome` → `Extensions` → `Developer Mode` → `Load unpacked`
- Select the `dist`/ folder to load your extension
- Open any Gmail email, and you will be prompted to authorize and set your timezone

Once set up, you're ready to use the Gmail Summarizer!

## API Endpoints
- POST	/api/summary/per	
  - Generate per-email summaries
- POST	/api/summary/overall	
  - Return overall summary (Loads from the database)
- POST	/api/settings	
  - Update user summary time preferences

## Tech Stack
- Python 3.10+
- Flask API – REST API backend
- Google Firestore – NoSQL document storage
- Azure OpenAI – AI summarization models
- Gmail API – Email fetching

## System Architecture
### File Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Load environment variables and configs
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── db.py               # Firestore connection and helper functions
│   │   ├── models.py           # Data models (UserSettings, PerEmailSummary, etc.)
│   ├── gmail/
│   │   ├── __init__.py
│   │   ├── fetch_emails.py     # Fetch emails from Gmail API
│   ├── summarizer/
│   │   ├── __init__.py
│   │   ├── summary_checker.py  # Check missing per-email summaries
│   │   ├── run_summary.py      # Core logic: run per-email & overall summary
│   │   ├── azure_agent/
│   │   │   ├── __init__.py
│   │   │   ├── ai_agent.py      # per_summarize() and overall_summarize() AI backend
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API routes (if you expose backend)
│   │   ├── time_utils.py       # Convert the UTC time zone and the user local time
│   ├── scheduler/
│   │   ├── task_scheduler.py   # Scheduled auto-run based on user setting
│
├── test/                       # Tests files for each components in app folder
├── main.py                  # App entry point
├── requirements.txt
├── README.md
└── .env
```
