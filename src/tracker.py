from collections import defaultdict
from datetime import datetime
import pandas as pd
import pickle
import os
from typing import Any, Optional, List

from CryptoOracle import CryptoOracle
import plot_data_functions as hairyPlotter
from RepoInfo import RepoInfo


def load_data(
    token: str,
    project_repos: List[str], 
    start_date: datetime,
    end_date: datetime,
    pickle_data_interval: str,
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
        
        # write to pickle files
        if write_to_pickle:
            with open(commits_pickle, 'wb') as cp:
                pickle.dump(project_commits, cp)
            with open(price_pickle, 'wb') as pp:
                pickle.dump(token_data, pp)

    return token_data, project_commits


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


if __name__ == "__main__":
    # setup
    token="LRC"
    start_date = datetime(2021, 12, 20, 12, 00, 00)
    end_date = datetime(2021, 12, 27, 13, 00, 00)

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]

    token_data, project_commits = load_data(
        token,
        project_repos,
        start_date,
        end_date,
        pickle_data_interval = 'week',
        read_from_pickle = False,
        write_to_pickle = False
    )

    # it's levioSA
    hairyPlotter.show_commmit_plot(token_data, project_commits)