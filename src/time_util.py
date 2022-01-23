from datetime import timezone, datetime

def datetime_to_ms_timestamp(dt):
    return dt.replace(tzinfo=timezone.utc).timestamp() * 1000

def round_single_commit_by_time(dt, granularity_min = 5):
    """
    Takes a commit time and rounds it to the nearest 
    X minutes so we can align it with the 5min crypto prices.

    this function takes in MINUTES!
    returns DATETIME!
    """
    nearest_5min = int(granularity_min * round(dt.minute / granularity_min))
    rounded_commit_time = datetime(dt.year, dt.month, dt.day, dt.hour, nearest_5min if nearest_5min != 60 else 0)
    return rounded_commit_time