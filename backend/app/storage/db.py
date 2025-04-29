# app/storage/db.py

import os
from dotenv import load_dotenv
from google.cloud import firestore
from app.config import GOOGLE_APPLICATION_CREDENTIALS


# Get the path to your JSON key file
cred_path = GOOGLE_APPLICATION_CREDENTIALS

if not cred_path:
    raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS in .env")

# Set up Firestore client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
db = firestore.Client()


def save_tokens(user_id, access_token, refresh_token, expiry):
    db.collection("user_tokens").document(user_id).set({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expiry": expiry
    })

def get_tokens(user_id):
    doc = db.collection("user_tokens").document(user_id).get()
    return doc.to_dict() if doc.exists else None


def store_user_settings(user_id: str, settings: dict):
    """
    Stores user settings directly on the user document.
    Expected settings format:
    {
        "weekdayTime": "9:00 AM",
        "weekendTime": "11:00 AM",
        "timeZone": "UTC+08:00",
        "weekdays": ["monday", "wednesday", "friday"]
    }
    """
    user_ref = db.collection("users").document(user_id)
    user_ref.set({"settings": settings}, merge=True)


# add a function 
def get_user_setting(user_id:str):
    """
    Retrieves all user settings directly from the root of the document.
    Returns None if the document does not exist.
    """
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("settings", {})
    return None


def store_per_email_summary(user_id: str, email_data: dict):
    """
    email_data example:
    {
      "id": "msg-001",
      "sender_name": "Dr. Lin",
      "subject": "🧠 AI Ethics Workshop Reminder",
      "summary": "...",
      "attachment_names": [],
      "receiveAt": "2024-04-17 11:40:00 UTC",
      "category": "Event"
    }
    """
    email_id = email_data["id"]
    data_without_id = {k: v for k, v in email_data.items() if k != "id"} #not sure if need to keep the id 

    doc_ref = db.collection('users').document(user_id).collection('email_summaries').document(email_id)
    doc_ref.set(data_without_id)


def get_per_email_summary(user_id: str, email_id: str) -> dict:
    doc_ref = db.collection("users").document(user_id).collection("email_summaries").document(email_id)
    doc = doc_ref.get() #resore the id or not?? 
    return doc.to_dict() if doc.exists else None

def get_all_per_email_summaries(user_id: str) -> list:
    col_ref = db.collection("users").document(user_id).collection("email_summaries")
    docs = col_ref.stream()
    summaries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # restore ID ??
        summaries.append(data)
    return summaries

def store_overall_summary(user_id: str, overall_data: dict, last_email_timestamp: str):
    """
    overall_data example:
    {
      "overall_summary": [ ... ]  # list of category summaries
    }
    last_email_timestamp: "2024-04-17 11:40:00 UTC"
    """
    doc_ref = db.collection("users").document(user_id)
    doc_ref.set({
        "overall_summary": overall_data,
        "last_email_timestamp": last_email_timestamp
    }, merge=True)


def get_overall_summary(user_id: str) -> dict:
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return {
        "overall_summary": data.get("overall_summary", []),
        "last_email_timestamp": data.get("last_email_timestamp")
    }

def get_all_users():
    users_ref = db.collection('users')
    docs = users_ref.stream()
    return [doc.id for doc in docs]


# Deletion
def delete_user_data(user_id: str):
    user_doc_ref = db.collection("users").document(user_id)

    subcollections = user_doc_ref.collections()
    for subcol in subcollections:
        docs = subcol.stream()
        for doc in docs:
            doc.reference.delete()

    print(f"Deleting main user doc: {user_id}")
    user_doc_ref.delete()