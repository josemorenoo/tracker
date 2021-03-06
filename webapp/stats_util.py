from collections import defaultdict
from datetime import timedelta, datetime

import matplotlib  
# needed on mac otherwise crashes
#matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import pandas as pd
from typing import List, Any
import sys

GRANULARITY_MIN = {"5min": 5, "15min": 15, "1hour": 60, "1day": 24*60, "1week": 24*60*7}

class Stats:

    def calculate_day_token_close(self, token_data: pd.DataFrame):
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

    def calculate_running_number_of_authors(commits: List[Any]):
        """
        returns a list containing the number of authors,
        and a list of the timestamp whenever there is an increase in the number of authors in the project
        """
        authors = []
        authors_count = [0]
        prev_count_idx = 0
        new_author_timestamps = []
        for c in commits:
            author_name = c.author.name
            if author_name not in authors:
                authors.append(author_name)
                authors_count.append(authors_count[prev_count_idx]  + 1)
                prev_count_idx += 1
                new_author_timestamps.append(c.ms_timestamp)
        return authors_count, authors, new_author_timestamps





    def calculate_commit_count_in_range(self, commits: List[Any], granularity: str):
        if len(commits) == 0:
            return [], []

        if granularity not in GRANULARITY_MIN.keys():
            print("eedeeot")
            sys.exit("provided {granularity} not in {GRANULARITY_MIN}")

        first_commit_ts = int(commits[0].ms_timestamp)
        ms_interval_step = int(GRANULARITY_MIN[granularity] * 60000) # convert to milliseconds
        end_commits_ts = int(commits[-1].ms_timestamp)
        print(f"first commit ts: {first_commit_ts}\tend commit ts:{end_commits_ts}")

        ts_bucket_list = list(range(first_commit_ts, end_commits_ts, ms_interval_step))
        ts_bucket_list.pop() # remove the last bucket so that we get the same size

        bucket_counts_list = []
        for bucket_interval_start in ts_bucket_list:
            bucket_count = 0
            for commit in commits:
                commit_ts = commit.ms_timestamp
                if commit_ts < bucket_interval_start + ms_interval_step:
                    bucket_count += 1
                else:
                    bucket_counts_list.append(bucket_count)
                    break

        if (len(ts_bucket_list) != len(bucket_counts_list)):
            sys.exit(f"number of buckets {len(ts_bucket_list)} does not equal counts of each bucket: {len(bucket_counts_list)}")
        return ts_bucket_list, bucket_counts_list
                
    def calculate_lines_of_code_count(commits: List[Any]):
        """
        Returns a list containing the absolute count of lines of code after each commit.

        Note that if you pass in a range starting after the project count the exact 
        count of line of code will be incorrect (probably way less than real life)
        """
        if len(commits) == 0:
            return [], []
            
        LOC_by_timestamp = [[int(commits[0].insertions - commits[0].deletions), int(commits[0].ms_timestamp)],]

        prev_index = 0
        for c in commits[1:]:
            # commits can be made at the exact same time because we are looking at multiple repos, aggregate LOCs for commits made at the exact same time
            previous_timestamp = LOC_by_timestamp[prev_index][1]
            if c.ms_timestamp == previous_timestamp:
                LOC_by_timestamp[prev_index][0] += int(c.insertions - c.deletions)

            # if the timestamp is new, create a new LOCs entry
            else:
                existing_LOC = LOC_by_timestamp[prev_index][0]
                LOC_by_timestamp.append([ int(c.insertions - c.deletions + existing_LOC), int(c.ms_timestamp)])
                prev_index += 1

        # unpack
        lines_of_code, commit_ms_timestamp = zip(*LOC_by_timestamp)

        # find the smallest negative LOC value and increase all LOC counts by that value since you can't have negative LOCs
        # this will happen if you pick a range starting after the first project commit, which is likely
        min_LOC = min(lines_of_code)
        if min_LOC < 0:
            lines_of_code = [loc + abs(min_LOC) for loc in lines_of_code]

        return lines_of_code, commit_ms_timestamp

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
        return list(sorted_days), list(sorted_values)


        
if __name__ == "__main__":
    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]
    
    #from setup_data import load_data
    token_data, _, _ = load_data(
        'LRC',
        project_repos,
        start_date=datetime(2021, 12, 10, 12, 0, 0),
        end_date = datetime(2021, 12, 17, 12, 0, 0),
        pickle_data_interval='week',
        read_from_pickle=True,
        write_to_pickle=True
    )

    distinct_days_closing_price = Stats.calculate_day_token_close(token_data)
    #print(distinct_days_closing_price)
    print("The end")
    
