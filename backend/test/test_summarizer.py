from backend.app.summarizer.summary_checker import run_overall_summary, run_per_email_summary
from backend.app.storage.db import (
    get_overall_summary,
    delete_user_data,
    get_all_per_email_summaries
)
from datetime import datetime
from typing import List, Dict
import os, json, uuid

new_email_data = [

    {
        "id": "msg-001",
        "subject": "🧠 AI Ethics Workshop Reminder",
        "body": "Dear team,\n\nReminder: our AI Ethics workshop starts at 10am in Room 204. Don’t forget to bring your slides if you’re presenting.\n\nSee you there!\n\nBest,\nDr. Lin",
        "attachment_names": [],
        "from": {
            "display_name": "Dr. Lin",
            "email": "dr.lin@university.edu"
        },
        "internalDate": "1713354000000"  
    },
    {
        "id": "msg-002",
        "subject": "📢 Invitation to NLP Global Summit",
        "body": "Hi Jenny,\n\nYou’re invited to the NLP Global Summit on April 12, featuring speakers from OpenAI, Google, and Microsoft. Don’t miss out!\n\nRegister at: https://nlpsummit.com/register",
        "attachment_names": ["NLP_Summit_Brochure.pdf"],
        "from": {
            "display_name": "Conference Team",
            "email": "events@nlpsummit.com"
        },
        "internalDate": "1713287520000"  
    },
    {
        "id": "msg-003",
        "subject": "📊 April Budget Report",
        "body": "Hi team,\n\nAttached is the April budget report. Please review before Friday’s finance meeting.\n\nThanks,\nFinance Dept.",
        "attachment_names": ["April_Budget_Report.xlsx"],
        "from": {
            "display_name": "Finance Dept.",
            "email": "finance@company.com"
        },
        "internalDate": "1713174765000" 
    },
    {
        "id": "msg-004",
        "subject": "🍕 Lunch Order Reminder",
        "body": "Hi all,\n\nSubmit your lunch order by 11 AM via the shared form. Late submissions may not be included.\n\nThanks!",
        "attachment_names": [],
        "from": {
            "display_name": "Office Admin",
            "email": "admin@company.com"
        },
        "internalDate": "1713095730000" 
    },
    {
        "id": "msg-005",
        "subject": "Action Required: MFA Enrollment",
        "body": "Hello,\n\nTo enhance account security, all users are required to enroll in Multi-Factor Authentication by April 15.\n\nFollow this link: https://company.com/mfa-setup\n\nIT Support",
        "attachment_names": [],
        "from": {
            "display_name": "IT Support",
            "email": "it@company.com"
        },
        "internalDate": "1713038400000" 
    },
    {
        "id": "msg-006",
        "subject": "Take appointment",
        "body": "Hello Prof Tom,\n\n I want to take the appoinetment on May 16th to inquire about the internship oppotunity.\n\nPlease let me know if this time work for you, thank you!\n\nBest, \n\n Amy",
        "attachment_names": [],
        "from": {
            "display_name": "Amy Cho",
            "email": "amy@school.edu"
        },
        "internalDate": "1713038600000" 
    }

]

def load_mock_emails(filepath="../app/summarizer/azure_agent/mock_data/sample_emails.json"):
    base_dir = os.path.dirname(__file__)  # directory of test_summary.py
    full_path = os.path.join(base_dir, filepath)
    print("Loading from:", full_path)  # debug print
    with open(full_path, "r") as f:
        return json.load(f)


def test_per_email_and_overall_summary():
    # Set up test user and emails
    user_id = f"test_user_{uuid.uuid4().hex[:6]}"
    emails = load_mock_emails()


    print(f"\nRunning test for user: {user_id} with {len(emails)} emails")

    # Generate per-email summaries
    run_per_email_summary(user_id, emails)
    print(get_all_per_email_summaries(user_id))

    

    # 3️⃣ Generate overall summary
    result = run_overall_summary(user_id, new_email_data)
    assert result is True, "Overall summary generation failed"

    overall = get_overall_summary(user_id)
    print(get_overall_summary(user_id))
    assert overall is not None, "❌ No overall summary stored"
    assert "overall_summary" in overall, "❌ overall_summary key missing"
    assert isinstance(overall["overall_summary"], list), "❌ overall_summary not a list"
    print("✅ Overall summary OK")

if __name__ == "__main__":
    test_per_email_and_overall_summary()