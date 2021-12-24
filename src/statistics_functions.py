# functions useful for plotting data
import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import pickle
import pandas as pd
import os
from typing import List,Any

from collections import defaultdict
 

# functions for statistics

def main():
    print("\n\nTesting statistics functions")
    # load pickle files
    directory = os.getcwd() + "/"
    
    with open(directory + 'one_week_project_commits_pickle' , 'rb') as pickle_file:
        project_commits = pickle.load(pickle_file)
    with open(directory + 'one_week_token_data_pickle' , 'rb') as pickle_file:
        token_data = pickle.load(pickle_file)
    
    
    commit_count_per_day(project_commits)
    
    print("The end")
    
    
def calculate_daily_count(commits: List[Any]):
    # calculates the number of commits per day
    
    # make list of days
    daily_count = defaultdict(int)
    
    for commit in commits:
        date = f"{str(commit.committer_date.year)}-{str(commit.committer_date.month)}-{str(commit.committer_date.day)}"
        #print(date)
        daily_count[date] += 1
        
    return(daily_count)
    
    
if __name__ == "__main__":
    main()
    
