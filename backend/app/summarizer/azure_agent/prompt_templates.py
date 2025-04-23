OVERALL_SUMMARY_PROMPT = """
You are an assistant tasked with summarizing the email activity of a user.
Group the emails by category, and provide a short, clear summary per category using bullet points.
Be concise, include relevant attachment names, and keep the total summary under 150 words.

In this format:
- **{Category Name}**
  - {Concise overall summary}
  - {Show attachement name if exist or not showing}


Example for ouput:
- **2 emails for Meetings**
  - A product sync meeting has been scheduled with the team.  
  - Your 1:1 check-in with the engineering manager has been rescheduled.
  - Attachments: roadmap.pdf

- **1 email for Security**
  - A mandatory MFA enrollment is required for all users.


Emails:
{summaries}
"""

OVERALL_SUMMARY_PROMPT_1 = """
You are an assistant tasked with summarizing the email activity of a user.
Group the emails by category, and provide a short, clear summary per category using up to 5 bullet points.
Be concise and keep the total summary under 150 words.

In this format:
- **{Category Name}**
  - {Concise overall summary}


Example for ouput:
- **Meetings**
  - A product sync meeting has been scheduled with the team.  
  - Your 1:1 check-in with the engineering manager has been rescheduled.

- **Security**
  - A mandatory MFA enrollment is required for all users.


Emails:
{summaries}
"""

OVERALL_SUMMARY_PROMPT_2 = """
You are an assistant summarizing emails grouped by category. Be consise and keep the total summary under 300 words.

Input is a list of objects. Each object contains:
- category: the category name
- combined_summaries: all email content (summaries + attachments) in that category

Your task is to:
- Generate at least 1 and up to 5 clear and concise bullet points **per category**
- Output JSON with category name as the key and bullet points as a list of strings
- Do not include email counts or attachments — your only job is summarization
- Be professional and clear

Example Input:
{{
  "Meetings": "Product sync with team. Weekly stand-up....",
  "Security": "MFA setup required. Password change next week.",
  ...
}}


Example Output:
{{
  "Meetings": [
    "A product sync meeting is scheduled.",
    "Your 1:1 check-in has been rescheduled.",
    "Reminder for the weekly stand-up meeting."
  ], 
  ...
}}

Now generate the bullet points for the following input:
{summaries}
"""
