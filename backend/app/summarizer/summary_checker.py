from app.storage.db import db, store_per_email_summary, get_per_email_summary, store_overall_summary
from typing import List, Dict
from app.summarizer.azure_agent.ai_agent import per_summarize, overall_summarize
import datetime


def run_overall_summary(user_id: str, emails: List[Dict]):
    """
    Process per-email summaries if missing, then generate the overall summary.
    Returns the true if completed, or false if have issues.

    Orchestrates the full flow:
    1. Checks if each email has a per-summary
    2. If not, generates and stores it
    3. After all are done, generates and stores overall summary
    """
    # convert the data format returned by fetch_emails.py
    processed_emails = []
    for email in emails:
        # ensure the key fields exist
        processed_email = {
            "id": email.get("id", ""),
            "subject": email.get("subject", ""),
            "body": email.get("body", ""),
            "attachment_names": email.get("attachment_names", []),
            "from": email.get("from", {"display_name": "", "email": ""}),
            "receiveAt": email.get("received_at_utc", ""),  # use UTC time as standard
        }
        processed_emails.append(processed_email)
    
    email_ids = [email["id"] for email in processed_emails]
    missing_ids = [eid for eid in email_ids if get_per_email_summary(user_id, eid) is None]
    if missing_ids:
        missing_emails = [email for email in processed_emails if email["id"] in missing_ids]
        run_per_email_summary(user_id, missing_emails)

    # need final check again or prevent long running here? 
    
    still_missing = [eid for eid in email_ids if get_per_email_summary(user_id, eid) is None]
    if still_missing:
        print(f"Still missing summaries for: {still_missing}")
        return False


    per_summaries = [get_per_email_summary(user_id, eid) for eid in email_ids]
    overall_summarize_result = overall_summarize(per_summaries)

    # Get the latest timestamp from original emails
    # add a default timestamp, if no valid timestamp
    timestamp_list = [email.get("receiveAt") for email in per_summaries if email and "receiveAt" in email and email["receiveAt"]]
    last_timestamp = max(timestamp_list) if timestamp_list else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    store_overall_summary(user_id, overall_summarize_result, last_timestamp)
    print("Overall summary stored.") # debug use
    return True

def run_per_email_summary(user_id: str, emails: List[Dict]):
    summarized = per_summarize(emails)
    for result in summarized:
        store_per_email_summary(user_id, result)

