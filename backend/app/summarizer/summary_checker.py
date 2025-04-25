from backend.app.storage.db import store_per_email_summary, get_per_email_summary, store_overall_summary
from typing import List, Dict
from backend.app.summarizer.azure_agent.ai_agent import per_summarize, overall_summarize


def run_overall_summary(user_id: str, emails: List[Dict]):
    """
    Process per-email summaries if missing, then generate the overall summary.
    Returns the true if completed, or false if have issues.

    Orchestrates the full flow:
    1. Checks if each email has a per-summary
    2. If not, generates and stores it
    3. After all are done, generates and stores overall summary
    """
    email_ids = [email["id"] for email in emails]
    missing_ids = [eid for eid in email_ids if get_per_email_summary(user_id, eid) is None]
    if missing_ids:
        missing_emails = [email for email in emails if email["id"] in missing_ids]
        run_per_email_summary(user_id, missing_emails)

    # need final check again or prevent long running here? 
    
    still_missing = [eid for eid in email_ids if get_per_email_summary(user_id, eid) is None]
    if still_missing:
        print(f"Still missing summaries for: {still_missing}")
        return False


    per_summaries = [get_per_email_summary(user_id, eid) for eid in email_ids]
    overall_summarize_result = overall_summarize(per_summaries)

    #Get the latest timestamp from original emails
    last_timestamp = max(email["receiveAt"] for email in per_summaries)

    store_overall_summary(user_id, overall_summarize_result, last_timestamp)
    print("Overall summary stored.") # debug use
    return True

def run_per_email_summary(user_id: str, emails: List[Dict]):
    summarized = per_summarize(emails)
    for result in summarized:
        store_per_email_summary(user_id, result)

