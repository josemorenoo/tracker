from collections import defaultdict
import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from datetime import datetime
import pandas as pd
from typing import Any, Dict, List

from CryptoOracle import CryptoOracle
from RepoInfo import RepoInfo

import os
import pickle

def show_commmit_plot(token_data: pd.DataFrame, commits: List[Any]):
    p = token_data.plot(y='close', use_index=True)
    for commit in commits:
        p.axvline(x=commit.rounded_commit_time, color='g', linestyle='--', linewidth=0.1)
    plt.show()

def get_commits_from_all_repos(project_repos: List[str]):
    repos_commit_dictionary = defaultdict(list)

    for repo_url in project_repos:
        repo_info = RepoInfo(repo_url)
        commits: List[Any] = repo_info.get_commits_by_date(startDate, endDate)
        #repo_info.show_n_most_common_commit_messages(commits, n = 10)

        # round the time of each commit to the nearest 5 min interval
        time_rounded_commits: List[Any] = repo_info.round_commits(commits)
        
        # store commits for this given repo in the dictionary
        repos_commit_dictionary[repo_url] = time_rounded_commits
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


if __name__ == "__main__":
    # setup
    token="LRC"
    startDate = datetime(2021, 12, 23, 12, 00, 00)
    endDate = datetime(2021, 12, 24, 13, 00, 00)

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/protocols',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]
    repos_commit_dictionary = get_commits_from_all_repos(project_repos)
    project_commits: List[Any] = gather_project_commits(repos_commit_dictionary)

    # get the crypto token price data as a dataframe
    crypto_oracle = CryptoOracle(token)
    token_data: pd.DataFrame = crypto_oracle.get_token_price_df(startDate, endDate)

    # visualize
    #show_commmit_plot(token_data, project_commits)
    
    # load pickle files
    directory = os.getcwd() + "/"
    with (directory + 'one_day_project_commits_pickle', 'wb') as f:
        pickle.dump(project_commits, f)