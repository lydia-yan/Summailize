# read user's settings from the database
# add a clock base on user's settings
# run the tasks based on the clock automatically    

import threading
import time
import schedule
import logging
from datetime import datetime, timedelta
import pytz
import os

from app.storage.db import get_user_setting, get_all_users
from app.api.time_utils import get_trigger_time
from app.summarizer.summary_checker import run_overall_summary

# configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSummaryScheduler:
    def __init__(self):
        self.scheduler_thread = None
        self.is_running = False
        self.jobs = {}  # user id to scheduler task mapping
    
    def start(self):
        """start the scheduler"""
        if self.is_running:
            logger.warning("scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("email summary scheduler is started")
        
        # initialize the task scheduler for all users
        self.update_all_user_schedules()
    
    def stop(self):
        """stop the scheduler"""
        if not self.is_running:
            logger.warning("scheduler is not running")
            return
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        schedule.clear()
        self.jobs = {}
        logger.info("email summary scheduler is stopped")
    
    def _run_scheduler(self):
        """run the scheduler main loop"""
        # 强制设置环境变量为UTC时区
        os.environ['TZ'] = 'UTC'
        time.tzset()  # 应用时区变更
        logger.info("Forced timezone to UTC for scheduler")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def update_all_user_schedules(self):
        """update the task scheduler for all users"""
        users = get_all_users()
        logger.info(f"update the task scheduler for {len(users)} users")
        
        for user_id in users:
            self.update_user_schedule(user_id)
    
    def update_user_schedule(self, user_id):
        """update the task scheduler for a single user"""
        # clear the existing tasks
        if user_id in self.jobs:
            for job in self.jobs[user_id]:
                schedule.cancel_job(job)
            del self.jobs[user_id]
        
        # get the user settings
        settings = get_user_setting(user_id)
        if not settings:
            logger.warning(f"user {user_id} has no settings, skip the scheduler")
            return
        
        # extract the necessary information from the user settings
        weekday_time = settings.get("weekdayTime", "9:00 AM")
        time_zone = settings.get("timeZone", "UTC+08:00")
        weekdays = settings.get("weekdays", ["monday", "wednesday", "friday"])
        
        # create the task scheduler for each weekday
        self._schedule_user_task(user_id, weekday_time, time_zone, weekdays)
        
        # if there is weekend settings, create the task scheduler for weekends
        weekend_time = settings.get("weekendTime")
        if weekend_time:
            weekend_days = ["saturday", "sunday"]
            weekend_days = [day for day in weekend_days if day not in weekdays]
            if weekend_days:
                self._schedule_user_task(user_id, weekend_time, time_zone, weekend_days)
    
    def _schedule_user_task(self, user_id, time_str, timezone_str, days):
        """create the task scheduler for the user at the specified date and time"""
        # calculate the trigger time (advance 10 minutes)
        trigger_dt = get_trigger_time(time_str, timezone_str, advance_minutes=10)
        trigger_time = trigger_dt.strftime("%H:%M")
        
        # day mapping
        day_mapping = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }

        # initialize the user's task list (if not exists)
        if user_id not in self.jobs:
           self.jobs[user_id] = []
           
        for day in days:
           if day in day_mapping:
               job = day_mapping[day].at(trigger_time).do(
                   self._execute_summary_task, user_id=user_id
               )
               self.jobs[user_id].append(job)
               
               logger.info(f"set the summary task for user {user_id} at {day} {trigger_time}(UTC)")
        
    
    def _execute_summary_task(self, user_id):
        """execute the summary task"""
        logger.info(f"start to generate the email summary for user {user_id}")
        try:
            # get the user settings
            from app.storage.db import get_user_setting
            settings = get_user_setting(user_id)
            
            if not settings:
                logger.error(f"user {user_id} has no settings, cannot generate the email summary")
                return
            
            # use Gmail API to get the recent emails
            from app.gmail.fetch_emails import get_emails_by_query
            
            # get the user timezone
            time_zone = settings.get("timeZone", "UTC+08:00")
            
            # get the query and max_emails from user settings
            query = settings.get("emailQueryPeriod", "newer_than:1d")
            max_emails = settings.get("maxEmailsPerSummary", 30)
            emails = get_emails_by_query(query, user_id, max_total=max_emails)
            
            # run the summary task
            success = run_overall_summary(user_id, emails)
            
            if success:
                logger.info(f"user {user_id} email summary generation is successful")
            else:
                logger.error(f"user {user_id} email summary generation is failed")
        except Exception as e:
            logger.exception(f"error when generating the email summary: {str(e)}")
    
    def handle_user_settings_update(self, user_id):
        """handle the user settings update"""
        logger.info(f"user {user_id} updated the settings, re-schedule the task")
        self.update_user_schedule(user_id)


# create a singleton instance
scheduler = EmailSummaryScheduler()

def start_scheduler():
    """start the scheduler"""
    scheduler.start()

def stop_scheduler():
    """stop the scheduler"""
    scheduler.stop()

def update_user_schedule(user_id):
    """update the user scheduler"""
    scheduler.update_user_schedule(user_id)
