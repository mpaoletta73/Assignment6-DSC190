import dateparser
from datetime import datetime, date, timedelta
import re
from dateutil.relativedelta import relativedelta

def parse(s, today=None):
    base_date = today if today is not None else date.today()
    relative_base = datetime.combine(base_date, datetime.min.time())
    
    # Handle "before" and "after" patterns
    before_match = re.match(r'(.+)\s+before\s+(.+)', s)
    after_match = re.match(r'(.+)\s+after\s+(.+)', s)
    
    if before_match or after_match:
        # Parse the quantity and the reference date separately
        if before_match:
            quantity_str, ref_date_str = before_match.groups()
            sign = -1  # before = subtract
        else:
            quantity_str, ref_date_str = after_match.groups()
            sign = 1   # after = add
        
        # Parse the reference date
        ref_date = parse(ref_date_str, today=today)
        if ref_date is None:
            return None
        
        # Parse the quantity (e.g., "5 days", "1 year and 2 months")
        delta = parse_quantity(quantity_str)
        if delta is None:
            return None
        
        # Apply the delta with appropriate sign
        if isinstance(delta, relativedelta):
            result = ref_date + (sign * delta)
        else:
            result = ref_date + timedelta(days=sign * delta)
        return result
    
    # Handle "next Tuesday", "last Monday", etc.
    weekday_match = re.match(r'(next|last|this)\s+(\w+)', s.lower())
    if weekday_match:
        direction, weekday_name = weekday_match.groups()
        target_weekday = get_weekday_number(weekday_name)
        if target_weekday is None:
            return None
        
        current_weekday = base_date.weekday()  # Monday=0, Sunday=6
        
        if direction == 'next':
            days_ahead = (target_weekday - current_weekday) % 7
            if days_ahead == 0:
                days_ahead = 7
        elif direction == 'last':
            days_ago = (current_weekday - target_weekday) % 7
            if days_ago == 0:
                days_ago = 7
            days_ahead = -days_ago
        else:  # 'this'
            days_ahead = (target_weekday - current_weekday) % 7
        
        return base_date + timedelta(days=days_ahead)
    
    # Try dateparser for simpler cases
    settings = {
        "RELATIVE_BASE": relative_base,
        "PREFER_DATES_FROM": 'future',
        "RETURN_AS_TIMEZONE_AWARE": False
    }
    
    res = dateparser.parse(s, settings=settings)
    
    if res is None:
        settings.pop("PREFER_DATES_FROM", None)
        res = dateparser.parse(s, settings=settings)
    
    return res.date() if res else None

def parse_quantity(quantity_str):
    """Parse expressions like '5 days', '1 year and 2 months' into a timedelta or relativedelta"""
    quantity_str = quantity_str.strip()
    
    # Handle "X days/weeks/etc."
    days_match = re.match(r'(\d+)\s+days?', quantity_str)
    if days_match:
        return int(days_match.group(1))
    
    weeks_match = re.match(r'(\d+)\s+weeks?', quantity_str)
    if weeks_match:
        return int(weeks_match.group(1)) * 7
    
    # Handle "X years and Y months"
    years_months_match = re.match(r'(\d+)\s+years?\s+and\s+(\d+)\s+months?', quantity_str)
    if years_months_match:
        years = int(years_months_match.group(1))
        months = int(years_months_match.group(2))
        return relativedelta(years=years, months=months)
    
    # Handle standalone "X years"
    years_match = re.match(r'(\d+)\s+years?', quantity_str)
    if years_match:
        return relativedelta(years=int(years_match.group(1)))
    
    # Handle standalone "X months"
    months_match = re.match(r'(\d+)\s+months?', quantity_str)
    if months_match:
        return relativedelta(months=int(months_match.group(1)))
    
    return None

def get_weekday_number(weekday_name):
    """Convert weekday name to number (Monday=0, Sunday=6)"""
    weekdays = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }
    return weekdays.get(weekday_name.lower())
