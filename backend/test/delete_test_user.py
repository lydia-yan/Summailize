from backend.app.summarizer.summary_checker import run_overall_summary, run_per_email_summary
from backend.app.storage.db import (
    delete_user_data
)

# write the test user id to delete
to_delete_user = ['test_user_88582d', 'test_user_dd6843',"test_user_ef972b"]

for id in to_delete_user:
    delete_user_data(id)
