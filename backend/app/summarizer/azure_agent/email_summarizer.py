import json
from openai import AzureOpenAI
from collections import defaultdict


from backend.app.summarizer.azure_agent.config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
from backend.app.summarizer.azure_agent.prompt_templates import OVERALL_SUMMARY_PROMPT,OVERALL_SUMMARY_PROMPT_1, OVERALL_SUMMARY_PROMPT_2

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-12-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

deployment = "gpt-4o-mini"

def group_summaries_by_category(per_email_results):
    category_summaries = defaultdict(list)
    category_attachments = defaultdict(list)

    for item in per_email_results:
        summary = item['summary']
        if item['attachment_names']:
            summary += f" Attachments: {', '.join(item['attachment_names'])}"
            category_attachments[item['category']].extend(item['attachment_names'])

        category_summaries[item['category']].append(summary)

    # Build final output structures
    grouped_result = {}
    category_info = {}

    for category in category_summaries:
        grouped_result[category] = " ".join(category_summaries[category])
        category_info[category] = {
            "email_count": len(category_summaries[category]),
            "attachments": category_attachments[category]
        }

    return grouped_result, category_info


def ai_summarize(formatted_input):
    prompt = OVERALL_SUMMARY_PROMPT_2.format(summaries=json.dumps(formatted_input, indent=2))

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("AI response not valid JSON")
        return {}


