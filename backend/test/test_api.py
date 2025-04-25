import sys
import os
import json
import requests
import time
from datetime import datetime

# add the project root directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# default API address
API_BASE_URL = "http://localhost:8000/api"

# test user ID
TEST_USER_ID = "test_api_user"

# test settings
TEST_SETTINGS = {
    "weekdayTime": "9:00 AM",
    "weekendTime": "11:00 AM",
    "timeZone": "UTC+08:00",
    "weekdays": ["monday", "wednesday", "friday"],
    "userId": TEST_USER_ID
}

# test email URL - use a short, valid format test ID
TEST_EMAIL_URL = "https://mail.google.com/mail/u/0/#inbox/18dcd3db57b4bcf1"

def test_save_settings():
    """
    test the save user settings API
    """
    print("\n===== test save user settings =====")
    try:
        response = requests.post(
            f"{API_BASE_URL}/settings",
            json=TEST_SETTINGS
        )
        
        print(f"status code: {response.status_code}")
        print(f"response content:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        return response.json().get("success", False)
    except Exception as e:
        print(f"error: {e}")
        return False

def test_get_overall_summary():
    """
    test the get overall summary API
    """
    print("\n===== test get overall summary =====")
    try:
        response = requests.post(
            f"{API_BASE_URL}/summarize/overall",
            json={"userId": TEST_USER_ID}
        )
        
        print(f"status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"response content:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            print(f"summary time: {data.get('dateTime', 'unknown')}")
        else:
            print(f"error response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"error: {e}")
        return False

def test_get_per_email_summary():
    """
    test the get per email summary API
    """
    print("\n===== test get per email summary =====")
    try:
        response = requests.post(
            f"{API_BASE_URL}/summarize/per",
            json={
                "emailUrl": TEST_EMAIL_URL,
                "userSettings": TEST_SETTINGS
            }
        )
        
        print(f"status code: {response.status_code}")
        print(f"response content:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"error: {e}")
        return False

def run_all_tests():
    """
    run all API tests
    """
    print("======= start API tests =======")
    
    # test save settings
    settings_success = test_save_settings()
    
    # wait for a few seconds for the server to process
    time.sleep(2)
    
    # test get overall summary
    overall_success = test_get_overall_summary()
    per_email_success = test_get_per_email_summary()
    
    # print the test results
    print("\n======= test results summary =======")
    print(f"save settings: {'success' if settings_success else 'failed'}")
    print(f"get overall summary: {'success' if overall_success else 'failed'}")
    print(f"get per email summary: {'success' if per_email_success else 'failed'}")
    print("==========================")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    
    print(f"using API address: {API_BASE_URL}")
    run_all_tests() 