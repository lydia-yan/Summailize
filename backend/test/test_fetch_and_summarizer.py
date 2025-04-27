import json
from app.gmail.fetch_emails import get_emails_by_query
from app.summarizer.summary_checker import per_summarize, run_overall_summary

def test_fetch_and_summarizer_pipeline():
    user_id = "jennyc28@uci.edu"  # CHANGE the to id that has token
    query = "newer_than:1d"  
    max_emails = 5

    # Step 1: fetch emails
    emails = get_emails_by_query(gmail_query=query, user_id=user_id, max_total=max_emails)
    
    assert len(emails) > 0, "Should fetch at least 1 email"

    # Step 3: overall summarize
    overall_summary = run_overall_summary(user_id, emails)
    print(f"✅ Overall summary:\n{overall_summary}")


    print(json.dumps({
        "emails_fetched": emails,
        "overall_summary": overall_summary
    }, ensure_ascii=False, indent=2))

test_fetch_and_summarizer_pipeline()