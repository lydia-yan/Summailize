# azure_ai_helper.py
import re
from datetime import datetime
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from backend.app.summarizer.azure_agent.config import AZURE_LANGUAGE_KEY , AZURE_LANGUAGE_ENDPOINT


def clean_email_body(text):
    # Remove signature and common greetings/closings
    text = re.split(r"--|\nThanks,|\nBest regards|\nRegards|\nSincerely|\nBests|\nBest", text)[0]
    return text.strip()

def authenticate_client():
    return TextAnalyticsClient(endpoint=AZURE_LANGUAGE_ENDPOINT, credential=AzureKeyCredential(AZURE_LANGUAGE_KEY))

def summarize_text(client, document):
    poller = client.begin_extract_summary(documents=document)
    results = poller.result()

    return results

def format_internal_date(internal_date_ms):
    timestamp = int(internal_date_ms) / 1000
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

def chunk_documents(documents, size=25):
    for i in range(0, len(documents), size):
        yield documents[i:i + size]

def summarize_emails(emails):
    """
    Accepts a list of Gmail-style email objects.
    Returns a list of dicts with summarized results.
    """
    is_single = not isinstance(emails, list)
    emails = [emails] if is_single else emails
    client = authenticate_client()
    results = []

    # Step 1: Prepare batch documents (max 25 at a time for Azure AI)
    documents = []
    email_meta = []  # to store corresponding id/sender for later

    for email_obj in emails:
        id = email_obj.get("id")
        sender_name = email_obj.get("from", {}).get("display_name", "")
        subject = email_obj.get("subject", "")
        body = email_obj.get("body", "")
        received_time = email_obj.get("internalDate")
        attachments = email_obj.get("attachment_names")

        content = clean_email_body(body)
        # Azure docs require IDs for tracking
        documents.append({
            "id": id,
            "language": "en",
            "text": content
        })

        email_meta.append({
            "id": id,
            "sender_name": sender_name,
            "subject": subject,
            "attachments": attachments,
            "received_time": format_internal_date(received_time)
        })

    # Step 2: Summarize and process in batches of 25
    for doc_chunk, meta_chunk in zip(chunk_documents(documents, 25),chunk_documents(email_meta, 25)):
        result_chunk = summarize_text(client, doc_chunk)

        # Step 3: Match the results back
        for i, res in enumerate(result_chunk):
            meta = email_meta[i]
            if not res.is_error:
                summary = " ".join([sentence.text for sentence in res.sentences])
            else:
                summary = "[ERROR] Could not summarize."

            results.append({
                "id": meta["id"],
                "sender_name": meta["sender_name"],
                "subject": meta["subject"],
                "summary": summary,
                "attachment_names": meta["attachments"],
                "receiveAt": meta["received_time"]
            })

    return results[0] if is_single else results


'''
Example of input of per email:
email_obj = {
    "id": "msg-002",
    "subject": "📢 Invitation to NLP Global Summit",
    "body": "Hi Jenny,\n\nYou’re invited to the NLP Global Summit on April 12, featuring speakers from OpenAI, Google, and Microsoft. Don’t miss out!\n\nRegister at: https://nlpsummit.com/register\n\nThanks,\nConference Team",
    "attachment_names": ["NLP_Summit_Brochure.pdf"],
    "from": {
        "display_name": "Conference Team",
        "email": "events@nlpsummit.com"
    },
    "internalDate": "1713287520000"  # 2024-04-16T14:32:00Z
}

Example of result output: 

{
  "id": "msg-002",
  "sender_name": "Conference Team",
  "subject": "📢 Invitation to NLP Global Summit",
  "summary": "You’re invited to the NLP Global Summit on April 12, featuring speakers from OpenAI, Google, and Microsoft.",
  "attachment_names": ["NLP_Summit_Brochure.pdf"],
  "receiveAt": "2024-04-16 14:32:00 UTC"
}
'''

