# backend/app/services/summary_service.py

from db import SessionLocal
from db.models import EmailCache
from app.gmail.fetch_emails import email_id_from_url, get_single_email, get_emails_by_query
# from services.jenny_client import summary_for_text, summarize_overall_emails
from services.settings_service import load_settings


def single_email_flow(email_url: str, user_id: str = "default") -> dict:
    """
    Handles the logic for summarizing a single Gmail email.
    - Parses the email ID from the URL.
    - Checks if the email summary is already cached in the database.
    - If not cached, fetches the email via Gmail API and generates a summary using Jenny.
    - Saves the summarized result in the database.
    - Returns the structured email object with summary.
    
    Args:
        email_url (str): Full Gmail URL pointing to a specific email.
        user_id (str): Identifier for the user requesting the summary.

    Returns:
        dict: Structured and summarized email data.
    """
    msg_id = email_id_from_url(email_url)
    if not msg_id:
        raise ValueError("Invalid Gmail URL")

    settings = load_settings(user_id)
    tz = settings.get("timeZone", "UTC+08:00")
    show_attachments = settings.get("showAttachments", True)

    # Check if the email summary is already cached
    with SessionLocal() as s:
        hit = s.get(EmailCache, msg_id)
        if hit:
            return hit.payload

    # Fetch the email and optionally remove attachments based on settings
    mail = get_single_email(msg_id, tz)
    if not show_attachments:
        mail["attachment_names"] = []

    # Generate summary using Jenny agent
    mail["summary"] = summary_for_text(mail["body"], settings)

    # Save the result to the database for caching
    with SessionLocal() as s:
        s.add(EmailCache(email_id=msg_id, user_id=user_id, payload=mail))
        s.commit()

    return mail


def overall_summary_flow(query: str, user_id: str = "default") -> dict:
    """
    Handles the logic for summarizing multiple Gmail emails in a time range.
    - Loads the user settings (timezone, display options).
    - Queries a list of emails within a time window using Gmail query syntax.
    - Iterates each email, generates summaries (or uses cache), and collects results.
    - Sends all summaries to Jenny to produce a single overall digest.
    - Returns the overall digest and all summarized emails.

    Args:
        query (str): Gmail search query (e.g. "newer_than:7d", or date range).
        user_id (str): Identifier for the user requesting the summary.

    Returns:
        dict: Dictionary including original query, list of summarized emails,
              and the overall summary string.
    """
    settings = load_settings(user_id)
    tz = settings.get("timeZone", "UTC+08:00")
    show_attachments = settings.get("showAttachments", True)

    # Fetch and clean up emails
    all_cleaned = get_emails_by_query(query, tz, max_total=100)

    for mail in all_cleaned:
        if not show_attachments:
            mail["attachment_names"] = []
        mail["summary"] = summary_for_text(mail["body"], settings)

    # Generate overall summary based on the summarized emails
    overall = summarize_overall_emails(all_cleaned, settings)

    return {
        "date_range": query,
        "emails": all_cleaned,
        "overall_summary": overall
    }
