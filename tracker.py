from datetime import datetime

from RepoInfo import RepoInfo

if __name__ == "__main__":
    loopring_repo_url = 'https://github.com/Loopring/loopring-web-v2'
    loopring_repo = RepoInfo(loopring_repo_url)

    #commits = loopring_repo.get_commits()

    less_commits = loopring_repo.get_commits_by_date(
        startDate=datetime(2021, 12, 20, 23, 25, 00),
        endDate=datetime(2021, 12, 20, 23, 30, 00)
    )
