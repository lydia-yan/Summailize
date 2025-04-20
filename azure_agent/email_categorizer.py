def decide_category_from_summary(summary_text):
    """
    Accepts summarized email text and returns a predicted category.
    Rule-based for now, easy to swap with ML later.
    """
    summary_text = summary_text.lower()

    category_keywords = {
        "Event": ["meeting", "workshop", "summit", "invitation", "conference", "calendar", "webinar"],
        "Reminder": ["reminder", "submit", "due", "deadline", "follow up", "respond"],
        "Finance": ["invoice", "budget", "payment", "billing", "report", "expense", "reimbursement"],
        "Security": ["mfa", "authentication", "password", "account", "enroll", "security"],
        "HR/People": ["hiring", "onboarding", "leave", "interview", "benefits", "vacation", "recruiting"],
        "Announcement": ["update", "announcement", "release", "launch", "newsletter"],
        "Action Required": ["action required", "important", "urgent", "immediate attention"],
        "Promotion": ["sale", "discount", "offer", "promotion", "deal", "coupon"],
        "Social": ["lunch", "celebration", "party", "gathering", "birthday", "congrats"],
    }

    for category, keywords in category_keywords.items():
        if any(keyword in summary_text for keyword in keywords):
            return category

    return "General"