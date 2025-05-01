# Summailize: Your Gmail AI Summarizer Agent

![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License: MIT](https://img.shields.io/badge/Mircrosoft-AI_Agent_Hackathon-orange.svg)
![Built with Azure AI](https://img.shields.io/badge/Azure-OpenAI-blue)



**Summailize** is a lightweight **AI agent** that automatically summarizes Gmail messages into short, actionable insights — all through a Chrome Extension powered by a FastAPI backend. It helps you stay on top of your inbox without reading long emails.

## Key Features
- AI-powered **autonomous summarization agent**
- Per-email and periodic digest summaries
- Google login & personalized data management
- Timezone-aware background scheduling
- Chrome extension frontend, FastAPI backend
- Modular pipeline with clean separation of logic for AI inference, storage, and scheduling

## Why It’s Useful
- Saves time by summarizing long emails
- Automatically generates periodic summaries daily (e.g. weekdays or weekend)
- Helps students, professionals, and teams avoid inbox overwhelm
- Works in the background once set up — **set it and forget it**

## Agent Architecture
This project follows an **agentic architecture** with the following components:

| Component  | Role |
| ------------- | ------------- |
| Frontend (Extension)  | Captures user context and email metadata  |
| Summarization Agent (Backend)  | Uses Azure OpenAI to generate summaries (per and overall)  |
| Azure LLM	  | Generates AI summaries  |
| Scheduler Agent | Triggers digest summaries based on setting time  |
| Firebase Storage	  | Stores per user summaries and preferences  |

## How to Run the Agent

### Prerequisites
- Node.js + npm
- Python 3.10+
- Azure OpenAI credentials
- Firebase project + `firebase_key.json`

### 
### 1. Clone the project

```bash
git clone https://github.com/lydia-yan/summailize.git
cd summailize
```

### 2. Set environment variables

Create a `.env` file and include:

```env
AZURE_LANGUAGE_KEY=your-azure-language-key
AZURE_LANGUAGE_ENDPOINT=...
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=...
GOOGLE_APPLICATION_CREDENTIALS=credentials/firebase_key.json
GOOGLE_CLIENT_SECRET_PATH=credentials/client_secret_.json
FLASK_SECRET_KEY=any-text-here
```

For more backend agent config, see [`backend/README.md`](./backend/README.md).

---

### 3. Start the Backend AI Agent (FastAPI)

```bash
cd backend
python main.py
```
API will be live at `http://localhost:8000`.

---

### 4. Build and Load the Chrome Extension Agent

```bash
npm install
npm run build
```
Then in Chrome:

- Visit `chrome://extensions/`
- Enable **Developer Mode**
- Click **Load unpacked** → select the `dist/` folder


### Example Agent Tasks

Here’s what your summarization agent can do:
- **Per-email Agent Task:**
    
    `POST /api/summarize/per` → Summarize one email
    
- **Digest Agent Task:**

    `POST /api/summarize/overall` → Summarize multiple emails for a timeframe

## Built With
- **FastAPI** for backend agents
- **Azure OpenAI** for summarization via GPT models
- **Firebase** for persistent storage
- **React** for frontend UI
- **Chrome Extension APIs** for Gmail interaction
- **Gmail API** for Gmail fetching

## Project Structure
```
.
├── backend/                # FastAPI-based AI agent logic (detailed README inside)
│   ├── app/
│   └── ...
├── frontend/               # Chrome extension frontend (React)
├── .env                    # Environment keys (excluded from Git)
├── README.md               # This file

```

## Where to Get Help
- Full backend documentation: [`backend/README.md`](./backend/README.md)
- Open an issue: [GitHub Issues](https://github.com/lydia-yan/summailize/issues)

## Developers
This project was developed for [Microsoft AI Agent Hackathon](https://microsoft.github.io/AI_Agents_Hackathon/).

<a href="https://github.com/Jennyyyy0212">
  <img src="https://github.com/Jennyyyy0212.png" width="80px;" alt="" />
</a>
<a href="https://github.com/lydia-yan">
  <img src="https://github.com/lydia-yan.png" width="80px;" alt="" />
</a>
<a href="https://github.com/flyjoanne">
  <img src="https://github.com/flyjoanne.png" width="80px;" alt="" />
</a>
<a href="https://github.com/nikoishere">
  <img src="https://github.com/nikoishere.png" width="80px;" alt="" />
</a>