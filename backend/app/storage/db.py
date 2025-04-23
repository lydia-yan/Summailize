# app/storage/db.py

import os
from dotenv import load_dotenv
from google.cloud import firestore

# Load variables from .env
load_dotenv()

# Get the path to your JSON key file
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not cred_path:
    raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS in .env")

# Set up Firestore client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
db = firestore.Client()

def store_user_settings(user_id: str, settings: dict):
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set({'settings': settings}, merge=True)
    # confirm the format of stoeage ??


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
        "overall_summary": overall_data["overall_summary"],
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
def delete_all_overall_summaries(user_id: str):
    """
    Deletes all documents under the 'overall_summaries' subcollection for a user.
    """
    col_ref = db.collection("users").document(user_id).collection("overall_summaries")
    docs = col_ref.stream()

    for doc in docs:
        doc.reference.delete()
        print(f"Deleted overall summary document {doc.id} for user {user_id}")

def delete_user_data(user_id: str):
    """
    Deletes the entire user document (including all subcollections and data).
    """
    user_ref = db.collection("users").document(user_id)
    user_ref.delete()
    print(f"Deleted all data for user {user_id}")