import json, os, time
from ai_agent import per_summarize, overall_summarize


def load_mock_emails(filepath="mock_data/sample_emails.json"):
    base_dir = os.path.dirname(__file__)  # directory of test_summary.py
    full_path = os.path.join(base_dir, filepath)
    print("Loading from:", full_path)  # debug print
    with open(full_path, "r") as f:
        return json.load(f)

# ⏱ Start timing
start_time = time.time()

mock_emails = load_mock_emails()
print(f"Number of emails: {len(mock_emails)}\n")

emails = per_summarize(mock_emails)
overall = overall_summarize(emails)
# ⏱ End timing
end_time = time.time()
duration = end_time - start_time

# 🖨️ Print results in pretty JSON
print("\n📧 Per-email summaries:")
print(json.dumps(emails, indent=2, ensure_ascii=False))
print()
print("\n🧾 Overall summary:")
print(json.dumps({"overall_summary": overall}, indent=2, ensure_ascii=False))
print()
print(f"\n⏱️ Runtime: {duration:.2f} seconds")