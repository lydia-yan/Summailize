from datetime import datetime, timedelta
import pytz
import re

def parse_timezone(timezone_str):
    """
    parse the timezone string, return the PyTZ timezone object
    for example: 'UTC+08:00' or 'UTC-05:00'
    """
    # handle the special case
    if timezone_str == 'UTC':
        return pytz.UTC
    
    # parse the UTC offset
    match = re.match(r'UTC([+-])(\d{2}):(\d{2})', timezone_str)
    if not match:
        # if the format is not matched, default return UTC
        return pytz.UTC
    
    sign, hours, minutes = match.groups()
    offset_hours = int(hours)
    offset_minutes = int(minutes)
    
    # calculate the total offset (seconds)
    total_offset = offset_hours * 3600 + offset_minutes * 60
    if sign == '-':
        total_offset = -total_offset
    
    # create the fixed offset timezone
    return pytz.FixedOffset(total_offset // 60)

def parse_time(time_str):
    """
    parse the time string, return the hour and minute
    for example: '9:00 AM' or '15:30'
    """
    # handle the time with AM/PM
    am_pm_match = re.match(r'(\d+):(\d+)\s*(AM|PM)', time_str, re.IGNORECASE)
    if am_pm_match:
        hours = int(am_pm_match.group(1))
        minutes = int(am_pm_match.group(2))
        am_pm = am_pm_match.group(3).upper()
        
        # adjust the hour
        if am_pm == 'PM' and hours < 12:
            hours += 12
        elif am_pm == 'AM' and hours == 12:
            hours = 0
        
        return hours, minutes
    
    # handle the 24-hour time
    match = re.match(r'(\d+):(\d+)', time_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # default return 9:00 AM
    return 9, 0

def convert_to_utc(time_str, timezone_str):
    """
    convert the user timezone time to UTC time
    
    parameters:
        time_str: the time string, for example: '9:00 AM'
        timezone_str: the timezone string, for example: 'UTC+08:00'
    
    return:
        the datetime object, represent the UTC time
    """
    user_tz = parse_timezone(timezone_str)
    hours, minutes = parse_time(time_str)
    
    # create the datetime object for today at the specified time
    now = datetime.now()
    user_time = datetime(
        year=now.year, 
        month=now.month, 
        day=now.day,
        hour=hours, 
        minute=minutes, 
        tzinfo=user_tz
    )
    
    # convert to UTC
    return user_time.astimezone(pytz.UTC)

def get_trigger_time(summary_time_str, timezone_str, advance_minutes=10):
    """
    calculate the trigger time, advance the specified minutes
    
    parameters:
        summary_time_str: the user set summary sending time
        timezone_str: the user timezone
        advance_minutes: the advance minutes to trigger, default 10 minutes
    
    return:
        the datetime object, represent the UTC time
    """
    utc_time = convert_to_utc(summary_time_str, timezone_str)
    # advance the specified minutes
    return utc_time - timedelta(minutes=advance_minutes)

def utc_to_user_timezone(utc_time_str, timezone_str):
    """
    Convert UTC time string to user's local timezone time string
    
    parameters:
        utc_time_str: UTC time string, for example: '2024-04-17 11:40:00 UTC'
        timezone_str: user's timezone string, for example: 'UTC+08:00'
    
    return:
        time string in user's timezone, for example: '2024-04-17 19:40:00'
    """
    # Check for empty/invalid inputs and use current time as fallback
    if not utc_time_str:
        # use current time as fallback
        current_utc = datetime.now(pytz.UTC)
        return current_utc.strftime('%Y-%m-%d %H:%M:%S')
    
    # Parse the UTC time string
    try:
        # Try to parse with UTC indicator
        utc_dt = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S UTC')
    except ValueError:
        try:
            # Try without UTC indicator
            utc_dt = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Try ISO format
                utc_dt = datetime.fromisoformat(utc_time_str)
            except (ValueError, TypeError):
                # If all formats fail, use current time
                utc_dt = datetime.now()
    
    # Ensure the datetime is timezone aware
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
    
    # Convert to user's timezone
    user_tz = parse_timezone(timezone_str)
    user_dt = utc_dt.astimezone(user_tz)
    
    # Format the date and time
    return user_dt.strftime('%Y-%m-%d %H:%M:%S')
