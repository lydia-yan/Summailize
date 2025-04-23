# Storage Module – Firestore database

This folder handles all interactions with **Google Firestore**, used to store:
- User settings (`summary_time`)
- Per-email summaries (`email_summaries` subcollection)
- Overall summaries (`overall_summary` field)
- Last email timestamp for overall summary (`last_email_timestamp` field)

## How to create the Firestore database 
### 1. Enable Firestore in Google Cloud Console

1. Go to: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Select or create a new **project**
3. In the sidebar, go to **Firestore** → click **Create database**
    - Choose **Start in production mode**
    - Select your location (e.g., us-central1)
    - Click **Create**

### 2. Set Up Service Account Credentials

1. In GCP Console, go to: **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
    - Name: `gmail-extension-service`
    - Role: **Cloud Datastore User**
3. Click **Create Key → JSON**
    - This downloads a `.json` key file (keep this safe!)
4. Save it in your project folder in root as `firebase_key.json`
5. Add the file name in the `.env` files
```
GOOGLE_APPLICATION_CREDENTIALS=./firebase_key.json
```
6. You're all set! 

### 3. Install Required Python Packages
(You can skip this step if you're using `requirements.txt` — all dependencies are already listed there.)
```bash
pip install google-cloud-firestore
```

## Database Structure
```
users/ (Collection)
├── user_abc123 (Document)
│   ├── summary_time: "08:00"
│   ├── last_email_timestamp: "2024-04-17 11:40:00 UTC"
│   ├── overall_summary: [  <-- summary grouped by category
│   │     {
│   │       category: "Event",
│   │       email_count: 3,
│   │       summary_bullets: [...],
│   │       attachments: [...]
│   │     },
│   │     ...
│   │   ]
│
│   └── email_summaries/ (Subcollection)
│       ├── msg-001 (Document)
│       │   ├── sender_name: "Dr. Lin"
│       │   ├── subject: "🧠 AI Ethics Workshop Reminder"
│       │   ├── summary: "Reminder: our AI Ethics workshop..."
│       │   ├── attachment_names: []
│       │   ├── receiveAt: "2024-04-17 11:40:00 UTC"
│       │   └── category: "Event"
│       ├── msg-002
│       ├── msg-003
│       └── ...
```
If you want check the data in the firebase, here's what you can do: 
1. Go to Firebase Console: [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Select Your Project. Make sure it’s the same project where you’re writing data via `google.cloud.firestore`.
3. In the left sidebar, go to **Build** > **Firestore Database**.
4. View your collections. You should see a collection named something like `users` if you used this in your code