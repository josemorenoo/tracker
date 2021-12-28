from collections import defaultdict
from datetime import datetime
import os
import pandas as pd
import pickle
from typing import Any, List, Optional

from CryptoOracle import CryptoOracle
from RepoInfo import RepoInfo
from timeUtil import datetime_to_ms_timestamp


def load_data(
    token: str,
    project_repos: List[str], 
    start_date: datetime,
    end_date: datetime,
    pickle_data_interval: Optional[str],
    read_from_pickle: bool = False,
    write_to_pickle: bool = True
):
    """
    write_to_pickle only matters when you're loading data from the internet.
    If you set read_from_pickle, no data is loaded from the internet, so write_to_pickle doesn't matter
    """
    pickle_basepath = os.getcwd() + f"/data/{token}/" + f"{pickle_data_interval}"
    commits_pickle = pickle_basepath + '_commits.pickle'
    price_pickle = pickle_basepath + '_price.pickle'

    if read_from_pickle:
        with open(commits_pickle, 'rb') as cp:
            project_commits = pickle.load(cp)
        with open(price_pickle, 'rb') as pp:
            token_data = pickle.load(pp)
    else:
        repos_commit_dictionary = get_commits_from_all_repos(project_repos, start_date, end_date)
        project_commits: List[Any] = gather_project_commits(repos_commit_dictionary)
        
        # get the crypto token price data as a dataframe
        crypto_oracle = CryptoOracle(token)
        token_data: pd.DataFrame = crypto_oracle.get_token_price_df(start_date, end_date)
        
        # add a column with datetime format
        token_data = create_datetime_and_ts_column(token_data)

        # write to pickle files
        if write_to_pickle:
            with open(commits_pickle, 'wb') as cp:
                pickle.dump(project_commits, cp)
            with open(price_pickle, 'wb') as pp:
                pickle.dump(token_data, pp)
        
    return token_data, project_commits

def create_datetime_and_ts_column(token_data: pd.DataFrame):
    # toke data comes in Timestamp type, but commits come in datetime, so we'll make a column
    # called datetime in token_data so that they have equivalent types.

    # make list of datetime objects    
    datetime_token_data = [pd.Timestamp.to_pydatetime(ts) for ts in token_data.index.tolist() ]
    token_data['datetime'] = datetime_token_data
    token_data['ms_timestamp'] = [datetime_to_ms_timestamp(dt) for dt in token_data['datetime'].to_list()]
    return token_data
    

def get_commits_from_all_repos(
    project_repos: List[str],
    startDate: Optional[datetime] = None,
    endDate: Optional[datetime] = None):

    repos_commit_dictionary = defaultdict(list)

    for repo_url in project_repos:
        if startDate and endDate:
            # faster, doesn't load EVERY commit:
            repo_info = RepoInfo(repo_url, startDate, endDate)
        else:
            # slower, load every commit
            repo_info = RepoInfo(repo_url)

        commits: List[Any] = repo_info.get_commits_by_date(startDate, endDate)
        #repo_info.show_n_most_common_commit_messages(commits, n = 10)
        
        # store commits for this given repo in the dictionary
        repos_commit_dictionary[repo_url] = commits
    return repos_commit_dictionary

def gather_project_commits(repos_commit_dictionary):
    """
    Take the dictionary which has repo_urls as key and list of commits as values,
    combine all lists of commits into a single list of project_commits
    """
    project_commits = []
    for list_of_repo_commits in repos_commit_dictionary.values():
        project_commits.extend(list_of_repo_commits)
    return project_commits