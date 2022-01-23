from collections import defaultdict
from datetime import datetime
import os
import pandas as pd
import pickle
from typing import Any, List, Optional

from .crypto_oracle import CryptoOracle
from .repo_info import RepoInfo
from .time_util import datetime_to_ms_timestamp

def create_token_data_directory(token):
    if not os.path.exists(f"data/{token}"):
        os.mkdir(f'data/{token}')

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
            project_commits_list = pickle.load(cp)

        with open(price_pickle, 'rb') as pp:
            token_data = pickle.load(pp)
    else:
        project_commits_list: List[Any] = get_list_of_project_commits(project_repos, start_date, end_date)
        
        # get the crypto token price data as a dataframe
        crypto_oracle = CryptoOracle(token)
        token_data: pd.DataFrame = crypto_oracle.get_token_price_df(start_date, end_date)
        
        # add a column with datetime format
        token_data = create_datetime_and_ts_column(token_data)

        # write to pickle files
        create_token_data_directory(token)
        if write_to_pickle:
            with open(commits_pickle, 'wb+') as cp:
                pickle.dump(project_commits_list, cp)
            with open(price_pickle, 'wb+') as pp:
                pickle.dump(token_data, pp)

    project_commits_df = create_commits_df(project_commits_list)
        
    return token_data, project_commits_list, project_commits_df

def create_datetime_and_ts_column(token_data: pd.DataFrame):
    # toke data comes in Timestamp type, but commits come in datetime, so we'll make a column
    # called datetime in token_data so that they have equivalent types.

    # make list of datetime objects    
    datetime_token_data = [pd.Timestamp.to_pydatetime(ts) for ts in token_data.index.tolist() ]
    token_data['datetime'] = datetime_token_data
    token_data['ms_timestamp'] = [datetime_to_ms_timestamp(dt) for dt in token_data['datetime'].to_list()]
    return token_data

def create_commits_df(project_commits_list: List[Any]):
    """
    Takes fields of interest in each Commit object and stores them all as a dataframe instead of a list of objects.
    This is mainly for plotting since plotly hovertemplate is easier to work with using a dataframe
    """
    msg_list = []
    author_list = []
    ms_timestamp_list = []
    in_main_branch_list = []
    files_changed_list = []
    deletions_list = []
    insertions_list = []
    for commit in project_commits_list:
        msg_list.append(commit.msg)
        author_list.append(commit.author.name)
        ms_timestamp_list.append(commit.ms_timestamp)
        in_main_branch_list.append(commit.in_main_branch)
        files_changed_list.append(commit.files)
        deletions_list.append(commit.deletions)
        insertions_list.append(commit.insertions)
    commits_df = pd.DataFrame({
        'msg': msg_list,
        'author': author_list,
        'ms_timestamp': ms_timestamp_list,
        'in_main_branch': in_main_branch_list,
        'files_changed': files_changed_list,
        'deletions': deletions_list,
        'insertions': insertions_list
    })
    return commits_df

    

def get_commits_from_all_repos_into_dict(
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

    # sort chronologically
    sorted_commits = sorted(project_commits, key=lambda c: c.ms_timestamp)
    print(f"project has {len(sorted_commits)} commits available")
    return sorted_commits

def get_list_of_project_commits(
    project_repos: List[str],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None):
    """
    Gets the commits for each repo in the project, gathers them all into a single list

    Args:
        project_repos (List[str]): [description]
        start_date (Optional[datetime], optional): [description]. Defaults to None.
        end_date (Optional[datetime], optional): [description]. Defaults to None.
        
    Returns:
        [List[commits]]
    """
    repos_commit_dictionary = get_commits_from_all_repos_into_dict(project_repos, start_date, end_date)
    project_commits_list: List[Any] = gather_project_commits(repos_commit_dictionary)
    return project_commits_list