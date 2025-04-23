# test_storage.py

from backend.app.storage.db import store_per_email_summary, store_overall_summary, get_overall_summary, get_per_email_summary, delete_user_data, store_user_settings, get_user_setting

test_user = "test_user_001"

# Sample per-email
sample_email = {
    "id": "msg-005",
    "sender_name": "IT Support",
    "subject": "Action Required: MFA Enrollment",
    "summary": "To enhance account security, all users are required to enroll...",
    "attachment_names": [],
    "receiveAt": "2024-04-13 20:00:00 UTC",
    "category": "Security"
}
store_per_email_summary(test_user, sample_email)

# Sample overall
overall = {
    "overall_summary": [
        {
            "category": "Security",
            "email_count": 1,
            "summary_bullets": [
                "All users must enroll in Multi-Factor Authentication by April 15..."
            ],
            "attachments": []
        }
    ]
}
store_overall_summary(test_user, overall, last_email_timestamp="2024-04-13 20:00:00 UTC")

test_settings = {
        "weekdayTime": "9:00 AM",
        "weekendTime": "11:00 AM",
        "timeZone": "UTC+08:00",
        "weekdays": ["monday", "wednesday", "friday"]
    }
store_user_settings(test_user, test_settings)

# Fetch back
test_id= "msg-005"
print(get_user_setting(test_user))
print(get_per_email_summary(test_user, test_id))
print(get_overall_summary(test_user))
# delete_user_data(test_user)
