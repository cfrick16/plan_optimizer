from datetime import datetime
"""
    Check if a timestamp falls within a given time range. Start and endTime are in the format of HH:MM.
    Handles overnight ranges as well.
"""  
def is_time_in_range(timestamp: datetime, start_time_str: str, end_time_str: str) -> bool:
    # Parse time strings to time objects
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()
    
    # Handle overnight range (e.g., 22:00 to 06:00)
    if start_time > end_time:
        return timestamp.time() >= start_time or timestamp.time() <= end_time
    
    return start_time <= timestamp.time() <= end_time
