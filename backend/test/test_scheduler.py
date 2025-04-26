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
TEST_USER_ID = "test_scheduler_user"

# test settings
TEST_SETTINGS = {
    "weekdayTime": "9:00 AM",
    "weekendTime": "11:00 AM",
    "timeZone": "UTC+08:00",
    "weekdays": ["monday", "wednesday", "friday"],
    "userId": TEST_USER_ID
}

# log config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# backend API address
API_BASE_URL = "http://localhost:8000/api"

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

def test_scheduler_with_frontend_settings():
    """test the various configurations that the frontend can actually set"""
    # create the test user ID
    test_user_id = f"test_scheduler_{uuid.uuid4().hex[:6]}"
    print(f"\n===== test user ID: {test_user_id} =====")
    
    # simulate the various configurations that the frontend can actually set
    test_cases = [
        {
            "name": "workday morning, weekend evening",
            "settings": {
                "userId": test_user_id,
                "weekdayTime": "9:00 AM",
                "weekendTime": "5:00 PM",
                "timeZone": "UTC+08:00",
                "weekdays": ["monday", "wednesday", "friday"]
            }
        },
        {
            "name": "same time every day",
            "settings": {
                "userId": test_user_id,
                "weekdayTime": "10:00 AM",
                "timeZone": "UTC+08:00",
                "weekdays": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            }
        },
        {
            "name": "customized email query and number of emails",
            "settings": {
                "userId": test_user_id,
                "weekdayTime": "8:30 AM",
                "timeZone": "UTC-05:00",  # test different timezones
                "weekdays": ["tuesday", "thursday"],
                "emailQueryPeriod": "newer_than:7d",  # query the emails in the last 7 days
                "maxEmailsPerSummary": 50  # maximum 50 emails per summary
            }
        }
    ]
    
    # test the direct storage of the settings through the API
    def test_api_storage(settings):
        try:
            response = requests.post(
                f"{API_BASE_URL}/settings",
                json=settings
            )
            print(f"API response status code: {response.status_code}")
            if response.status_code == 200:
                print(f"API response content: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"API error response: {response.text}")
                return False
        except Exception as e:
            print(f"API request exception: {e}")
            return False
    
    # test the direct storage of the settings through the function
    def test_direct_storage(settings):
        try:
            result = store_user_settings(settings["userId"], settings)
            stored_settings = get_user_setting(settings["userId"])
            print(f"direct storage result: {result}")
            print(f"get the stored settings: {stored_settings}")
            return result
        except Exception as e:
            print(f"direct storage exception: {e}")
            return False
    
    # test if the scheduler correctly creates the task
    def test_scheduler_update(settings):
        try:
            # call the scheduler update
            update_user_schedule(settings["userId"])
            
            # check if the scheduler has the task
            print(f"does the user have a scheduler task: {settings['userId'] in scheduler.jobs}")
            if settings["userId"] in scheduler.jobs:
                job = scheduler.jobs[settings["userId"]]
                print(f"the next run time of the task: {job.next_run}")
                # manually trigger the task test (not waiting for the scheduled time)
                print("manually trigger the task test...")
                scheduler._execute_summary_task(settings["userId"])
            return settings["userId"] in scheduler.jobs
        except Exception as e:
            print(f"scheduler test exception: {e}")
            return False
    
    # run all test cases
    for case in test_cases:
        print(f"\n===== test case: {case['name']} =====")
        
        # test the storage of the settings through the API
        print("1. test the storage of the settings through the API")
        api_result = test_api_storage(case["settings"])
        
        print("\n2. test the storage of the settings through the function")
        direct_result = test_direct_storage(case["settings"])
        
        print("\n3. test the scheduler update")
        scheduler_result = test_scheduler_update(case["settings"])
        
        # print the test result
        print(f"\ntest result: API storage={'success' if api_result else 'failed'}, "
              f"direct storage={'success' if direct_result else 'failed'}, "
              f"scheduler update={'success' if scheduler_result else 'failed'}")
        
        # wait for a while before the next test
        time.sleep(2)
    
    # clean up the test data
    delete_user_data(test_user_id)
    print(f"\nclean up the test data for user {test_user_id}")

def diagnose_frontend_issues():
    """diagnose the issue that the frontend settings cannot be stored"""
    print("\n===== diagnose the frontend settings storage issue =====")
    
    # 1. test the API connection
    try:
        response = requests.get(f"{API_BASE_URL}")
        print(f"1. API connection test: {'success' if response.status_code in [200, 404] else 'failed'} (status code: {response.status_code})")
    except Exception as e:
        print(f"1. API connection test: failed (error: {e})")
    
    # 2. test the simple settings storage
    test_user = "diagnose_user"
    simple_settings = {
        "userId": test_user,
        "weekdayTime": "9:00 AM",
        "timeZone": "UTC+08:00",
        "weekdays": ["monday"]
    }
    
    try:
        print("\n2. test the simple settings storage:")
        response = requests.post(
            f"{API_BASE_URL}/settings",
            json=simple_settings
        )
        print(f"    status code: {response.status_code}")
        print(f"    response content: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.status_code == 200 else response.text}")
    except Exception as e:
        print(f"    test failed: {e}")
    
    # 3. check the data in the database
    try:
        print("\n3. check the data in the database:")
        stored = get_user_setting(test_user)
        print(f"    stored settings: {stored}")
    except Exception as e:
        print(f"    check failed: {e}")
    
    # 4. directly use the function to store
    try:
        print("\n4. directly use the function to store:")
        result = store_user_settings(test_user, simple_settings)
        print(f"    storage result: {result}")
        stored = get_user_setting(test_user)
        print(f"    stored settings: {stored}")
    except Exception as e:
        print(f"    direct storage failed: {e}")
    
    # clean up the diagnostic data
    delete_user_data(test_user)

if __name__ == "__main__":
    # first diagnose the frontend settings issue
    diagnose_frontend_issues()
    
    # then test the scheduler functionality
    test_scheduler_with_frontend_settings() 