# backend/app/gmail/time_utils.py
"""
Time-conversion helpers for Gmail internalDate (ms since epoch).
"""

from datetime import datetime, timedelta, timezone
from typing import Union


def internal_ms_to_utc_iso(ms: Union[str, int]) -> str:
    """Return an ISO-8601 UTC string from Gmail internalDate."""
    dt = datetime.utcfromtimestamp(int(ms) / 1000).replace(tzinfo=timezone.utc)
    return dt.isoformat()        # e.g. 2025-04-23T01:00:00+00:00


def internal_ms_to_tz_iso(ms: Union[str, int], tz_offset: str) -> str:
    """
    Convert internalDate (ms) to ISO string in a custom timezone.

    tz_offset examples:  "UTC+08:00",  "UTC-05:00"
    """
    sign = 1 if "+" in tz_offset else -1
    hours   = int(tz_offset[4:6])
    minutes = int(tz_offset[7:9])
    offset  = timedelta(hours=sign * hours, minutes=sign * minutes)

    base = datetime.utcfromtimestamp(int(ms) / 1000)
    local = (base + offset).replace(tzinfo=timezone(offset))
    return local.isoformat()     # e.g. 2025-04-23T09:00:00+08:00