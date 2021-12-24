import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from datetime import datetime
from typing import Any, List

from CryptoOracle import CryptoOracle
from RepoInfo import RepoInfo

def show_commmit_plot(token_data, time_rounded_commits: List[Any]):
    p = token_data.plot(y='close', use_index=True)
    for commit in time_rounded_commits:
        p.axvline(x=commit.rounded_commit_time, color='g', linestyle='--', linewidth=0.1)
    plt.show()


if __name__ == "__main__":
    # setup
    token="LRC"
    startDate = datetime(2020, 12, 1, 23, 25, 00)
    endDate = datetime(2021, 12, 23, 23, 54, 00)
    repo_url = 'https://github.com/Loopring/loopring-web-v2'

    # parse the repo for commits
    repo_info = RepoInfo(repo_url)
    commits = repo_info.get_commits_by_date(startDate, endDate)

    # round the time of each commit to the nearest 5 min interval,
    # creates .rounded_commit_time property for commit object
    time_rounded_commits = repo_info.round_commits(commits)

    # get the crypto token price data
    crypto_oracle = CryptoOracle(token)
    token_data = crypto_oracle.get_token_price_df(startDate, endDate)


    # visualize
    show_commmit_plot(token_data, time_rounded_commits)