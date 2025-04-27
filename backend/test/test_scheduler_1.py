import sys
import os
import time
from datetime import datetime, timedelta
import unittest
import json
import uuid
import logging
import requests

# add the project root directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.db import store_user_settings, get_user_setting, delete_user_data
from app.api.time_utils import get_trigger_time, utc_to_user_timezone
from app.scheduler.task_scheduler import EmailSummaryScheduler, start_scheduler, stop_scheduler, update_user_schedule, scheduler

# 
TEST_USER_ID = "jennyc28@uci.edu"

# test settings
TEST_SETTINGS = {
    "weekdayTime": "9:00 AM",
    "weekendTime": "11:10 PM",
    "timeZone": "UTC+00:00",
    "weekdays": ["monday", "wednesday", "friday"],
    "userId": TEST_USER_ID
}

# log config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# backend API address
API_BASE_URL = "http://localhost:8000/api"


# Step 2: Monkey-patch the _schedule_user_task to run every 5 seconds
def quick_test_schedule(self, user_id, time_str, timezone_str, days):
    job = scheduler.every(5).seconds.do(self._execute_summary_task, user_id=user_id)
    self.jobs[user_id] = job
    print(f"[TEST] Scheduled task for {user_id} every 5 seconds.")

# Replace the real _schedule_user_task temporarily
scheduler._schedule_user_task = quick_test_schedule.__get__(scheduler)

# Step 3: Start the scheduler
start_scheduler()

# Step 4: Wait and observe (run for 20 seconds)
time.sleep(20)

# Step 5: Stop the scheduler
stop_scheduler()

print("✅ Test Completed.")
