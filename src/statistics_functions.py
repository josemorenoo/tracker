from collections import defaultdict
from datetime import date, timedelta, datetime

import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import pickle
import pandas as pd
import os
from typing import List, Any
from setup import load_data

def main():
    print("\n\nTesting statistics functions")

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]
    
    token_data, _ = load_data(
        'LRC',
        project_repos,
        start_date=datetime(2021, 12, 10, 12, 0, 0),
        end_date = datetime(2021, 12, 17, 12, 0, 0),
        pickle_data_interval='week',
        read_from_pickle=True,
        write_to_pickle=True
    )

    distinct_days_closing_price = calculate_day_token_close(token_data)
    #print(distinct_days_closing_price)
    print("The end")
    
def calculate_day_token_close(token_data: pd.DataFrame):
    """
    Gets the closing price for each unique day, returns list of tuples.
    Example: 
    [
        ('2021-12-10', 2.3026),
        ('2021-12-11', 2.4234),
        ('2021-12-12', 2.4562),
        ('2021-12-13', 2.0972)
    ]
    """

    # unpack all (datetime, closing_price) from dataframe into a list of tuples
    all_closing_prices = [(str(r['datetime']).split(' ')[0], r['close']) for _, r in token_data.iterrows()]
    
    # create a dictionary of 'seen' days
    days_seen = defaultdict(str)
    days_seen[all_closing_prices[0][0]] = 'seen'

    # iterate over each day, if you see a new one get the price from the previous day
    distinct_days_closing_price = []
    for index, day_and_price in enumerate(all_closing_prices):
        day = day_and_price[0]
        if day not in days_seen:
            distinct_days_closing_price.append(all_closing_prices[index-1])
            days_seen[day] = 'seen'
    
    return distinct_days_closing_price
            

    
def calculate_daily_commit_count(commits: List[Any]):
    """
    Returns a list of sorted days, and a list of corresponding commits per day
    """
    
    # make list of days
    daily_count = defaultdict(int)
    
    # calculate number of commits in a day using a dictionary
    for commit in commits:    
        date = f"{str(commit.committer_date.year)}-{str(commit.committer_date.month)}-{str(commit.committer_date.day)}"
        daily_count[date] += 1
        
    # sort dates to calculate start_date and end_date 
    sorted_dates = sorted(daily_count.keys(), key=lambda x : datetime.strptime(x, '%Y-%m-%d'))
    start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d')
    end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d')
    
    # populate days that did not have a commit with 0 by iterating over the entire range
    def daterange(start_date, end_date):
        # creates a string with all dates from start to end date
        # must be a python date type
        for n in range( int((end_date - start_date ).days) + 1):
            yield start_date + timedelta(n)
            
    for single_date in daterange(start_date, end_date):
        single_date_string = f"{str(single_date.year)}-{str(single_date.month)}-{str(single_date.day)}"
        if single_date_string not in daily_count:
            daily_count[single_date_string] = 0
    
    # get sorted lists of days and values
    # creates list of tuples: [(date, commit_count), (), ...]
    daily_count_sorted_list = sorted(
        [(datetime.strptime(date,'%Y-%m-%d'), commit_count) for date, commit_count in daily_count.items()], 
        key = lambda tupey: tupey[0]
    )
    
    # unpack list of tuples into two separate lists
    # so [(1, a), (2, b)] becomes [1, 2] and [a, b]
    sorted_days, sorted_values = zip(*daily_count_sorted_list)
    return list(sorted_days), sorted_values


        
        
    
    
if __name__ == "__main__":
    main()
    
