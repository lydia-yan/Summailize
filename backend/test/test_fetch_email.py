import json
from app.gmail.fetch_emails import get_emails_by_query

def test_get_emails_real():
    user_id = "jennyc28@uci.edu"  # put a user id that has token in db
    query = "newer_than:1d"  # the newsest 1 day emails
    result = get_emails_by_query(gmail_query=query, user_id=user_id, max_total=5)

    print(f"✅ Got {len(result)} emails!")

    # check if the return is list
    assert isinstance(result, list)

    # check column
    if result:
        first = result[0]
        assert "id" in first
        assert "subject" in first
        assert "body" in first
        assert "attachment_names" in first
        assert "from" in first
        assert "display_name" in first["from"]
        assert "email" in first["from"]
        assert "internalDate" in first

    print(json.dumps(result, ensure_ascii=False, indent=2))


test_get_emails_real()


