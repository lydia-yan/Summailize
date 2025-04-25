import sys
import os
import time
from datetime import datetime, timedelta
import unittest
import json

# add the project root directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.db import store_user_settings, get_user_setting, delete_user_data
from app.api.time_utils import get_trigger_time, utc_to_user_timezone
from app.scheduler.task_scheduler import EmailSummaryScheduler, start_scheduler, stop_scheduler

# 
TEST_USER_ID = "test_scheduler_user"

# test settings
TEST_SETTINGS = {
    "weekdayTime": "9:00 AM",
    "weekendTime": "11:00 AM",
    "timeZone": "UTC+08:00",
    "weekdays": ["monday", "wednesday", "friday"],
    "userId": TEST_USER_ID
}

class TestScheduler(unittest.TestCase):
    
    def setUp(self):
        # clean up the previous test data
        try:
            delete_user_data(TEST_USER_ID)
        except Exception:
            pass
        
        # store the test settings
        store_user_settings(TEST_USER_ID, TEST_SETTINGS)
    
    def tearDown(self):
        # clean up the test data
        try:
            delete_user_data(TEST_USER_ID)
        except Exception:
            pass
    
    def test_time_utils(self):
        """test the time utility functions"""
        # test UTC to user timezone
        utc_time = "2024-04-17 11:40:00 UTC"
        user_timezone = "UTC+08:00"
        local_time = utc_to_user_timezone(utc_time, user_timezone)
        
        # verify the conversion is correct (UTC+8 should add 8 hours)
        print(f"UTC time: {utc_time}")
        print(f"local time (UTC+08:00): {local_time}")
        
        # test the calculation of the trigger time
        summary_time = "9:00 AM"
        trigger_time = get_trigger_time(summary_time, user_timezone)
        print(f"summary time: {summary_time} (UTC+08:00)")
        print(f"trigger time (10 minutes before): {trigger_time.strftime('%H:%M:%S')} (UTC)")
    
    def test_scheduler_init(self):
        """test the initialization of the scheduler"""
        # create the scheduler instance
        scheduler = EmailSummaryScheduler()
        
        # start the scheduler
        scheduler.start()
        print("scheduler started")
        
        # wait for the scheduler to initialize
        time.sleep(2)
        
        # update the user schedule
        print("update the user schedule...")
        scheduler.update_user_schedule(TEST_USER_ID)
        
        # check if the job is created
        self.assertIn(TEST_USER_ID, scheduler.jobs)
        print(f"successfully created the scheduler task for user {TEST_USER_ID}")
        
        # stop the scheduler
        scheduler.stop()
        print("scheduler stopped")
    
    def test_scheduler_singleton(self):
        """test the singleton function of the scheduler"""
        # start the scheduler
        start_scheduler()
        print("scheduler started by the singleton function")
        
        # wait for a while
        time.sleep(2)
        
        # stop the scheduler
        stop_scheduler()
        print("scheduler stopped by the singleton function")


def manual_test():
    """manual test function, for interactive testing"""
    print("=============== manual test mode ===============")
    
    # store the test settings
    print(f"store the settings for user {TEST_USER_ID}...")
    store_user_settings(TEST_USER_ID, TEST_SETTINGS)
    
    # read the settings to confirm
    settings = get_user_setting(TEST_USER_ID)
    print(f"read the settings: {json.dumps(settings, indent=2)}")
    
    # test the time conversion
    print("\ntest the time conversion:")
    utc_time = "2024-04-17 11:40:00 UTC"
    user_timezone = settings.get("timeZone", "UTC+00:00")
    local_time = utc_to_user_timezone(utc_time, user_timezone)
    print(f"UTC time: {utc_time}")
    print(f"local time ({user_timezone}): {local_time}")
    
    # test the calculation of the trigger time
    print("\ntest the calculation of the trigger time:")
    summary_time = settings.get("weekdayTime", "9:00 AM")
    trigger_time = get_trigger_time(summary_time, user_timezone)
    print(f"set the summary time: {summary_time} ({user_timezone})")
    print(f"actual trigger time (10 minutes before): {trigger_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
    
    # start the scheduler
    print("\nstart the scheduler (will stop automatically in 5 seconds)...")
    start_scheduler()
    
    # wait for 5 seconds, then stop the scheduler
    time.sleep(5)
    stop_scheduler()
    print("scheduler stopped")
    
    print("=============== test completed ===============")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        manual_test()
    else:
        unittest.main() 