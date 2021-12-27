# functions useful for plotting data
from dataclasses import dataclass
import dataclasses
import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import pickle
import pandas as pd
import os
from typing import Counter, List,Any

from collections import defaultdict
 
# time date things
from datetime import date, timedelta, datetime



# functions for statistics

def main():
    print("\n\nTesting statistics functions")
    # load pickle files
    directory = os.getcwd() + "/"
    
    with open(directory + 'one_week_project_commits_pickle' , 'rb') as pickle_file:
        project_commits = pickle.load(pickle_file)
    with open(directory + 'one_week_token_data_pickle' , 'rb') as pickle_file:
        token_data = pickle.load(pickle_file)

    print("The end")
    
    
def calculate_daily_count(commits: List[Any]):
    # calculates the number of commits per day
    
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
    
