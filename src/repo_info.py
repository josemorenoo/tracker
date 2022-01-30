from pydriller import Repository

from collections import Counter
from datetime import datetime
import pytz
from tqdm import tqdm
from typing import Any, List, Optional

from .commit_handler import CommitHandler

class RepoInfo:

    def __init__(self, githubRepoUrl: str, startDate: Optional[datetime] = None, endDate: Optional[datetime] = None):
        self.githubRepoUrl = githubRepoUrl

        ch = CommitHandler()

        # get all the commits
        if startDate and endDate:
            self.commits = [ch.create_commit(commit) for commit in tqdm(Repository(self.githubRepoUrl, since=startDate, to=endDate).traverse_commits())]
        else:
            self.commits = [ch.create_commit(commit) for commit in tqdm(Repository(self.githubRepoUrl).traverse_commits())]

    def get_commits(self) -> List[Any]:
        return self.commits

    def get_commits_by_date(self, startDate = None, endDate = None) -> List[Any]:
        norm_dt = lambda dt: dt.replace(tzinfo=pytz.UTC)
        if startDate:
            startDate = norm_dt(startDate)
        if endDate:
            endDate = norm_dt(endDate)

        if startDate and endDate:
            print("filtering through {} commits between start: {}, end: {}".format(str(len(self.commits)), str(startDate), str(endDate)))
            filtered = list(filter(lambda c: norm_dt(c.committer_date) > startDate and norm_dt(c.committer_date) < endDate, self.commits))
            print("found {}\n".format(str(len(filtered))))
            return filtered

        elif startDate and not endDate:
            print("filtering through {} commits between start: {}, end: {}".format(str(len(self.commits)), str(startDate), str(datetime.now())))
            filtered = list(filter(lambda c: norm_dt(c.committer_date) > startDate, self.commits))
            print("found {}\n".format(str(len(filtered))))
            return filtered
        elif not startDate and endDate:
            print("filtering through {} commits between start: {}, end: {}".format(str(len(self.commits)), str(self.commits[0].committer_date), str(endDate)))
            filtered = list(filter(lambda c: norm_dt(c.committer_date) < endDate, self.commits))
            print("found {}\n".format(str(len(filtered))))
            return filtered
        else:
            return self.commits

    def show_n_most_common_commit_messages(self, commits: List[Any], n: int = 10):
        """
        Shows the n most common commit messages,
        not used for anything other than utility
        """

        commit_messages = [c.msg for c in commits]
        print("{} most common commit messages for {} are:\n".format(n, self.githubRepoUrl))
        print(*list(Counter(commit_messages).most_common(n)), sep="\n")
        
