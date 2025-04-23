from email_cleaner import summarize_emails
from email_categorizer import decide_category_from_summary
from email_summarizer import group_summaries_by_category, ai_summarize

def per_summarize(emails):
    # Summerize per email and get the data
    summarized_results = summarize_emails(emails)

    # Add category to each summarized result
    for email in summarized_results if isinstance(summarized_results, list) else [summarized_results]:
        summary = email.get("summary", "")
        category = decide_category_from_summary(summary)
        email["category"] = category


    return summarized_results


def overall_summarize(emails):
    grouped_result, category_info = group_summaries_by_category(emails)
    summary_output = ai_summarize(grouped_result)

    # Combine everything into final JSON output
    final_output = []
    for category, bullets in summary_output.items():
        final_output.append({
            "category": category,
            "email_count": category_info[category]["email_count"],
            "summary_bullets": bullets,
            "attachments": category_info[category]["attachments"]
        })

    return final_output