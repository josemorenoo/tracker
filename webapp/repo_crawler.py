from pydriller import Repository

from collections import Counter
from datetime import datetime
import pytz
from tqdm import tqdm
from typing import Any, List, Optional

from .commit_handler import CommitHandler

class RepoInfo:

    def __init__(self,
        github_repo_url: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None):

        self.github_repo_url = github_repo_url

        ch = CommitHandler()

        # get all the commits
        if start_date and end_date:
            self.commits = [ch.create_commit(commit) for commit in tqdm(Repository(
                self.github_repo_url,
                since=start_date,
                to=end_date).traverse_commits())]
        else:
            self.commits = [ch.create_commit(commit) for commit in tqdm(Repository(
                self.github_repo_url).traverse_commits())]

    def get_commits(self) -> List[Any]:
        return self.commits

    def get_commits_by_date(self, start_date = None, end_date = None) -> List[Any]:
        norm_dt = lambda dt: dt.replace(tzinfo=pytz.UTC)
        if start_date:
            start_date = norm_dt(start_date)
        if end_date:
            end_date = norm_dt(end_date)

        if start_date and end_date:
            print("{}: filtering through {} commits between start: {}, end: {}".format(self.github_repo_url.split('/')[-1], str(len(self.commits)), str(start_date), str(end_date)))
            filtered = list(filter(lambda c: norm_dt(c.committer_date) > start_date and norm_dt(c.committer_date) < end_date, self.commits))
            print("found {}\n".format(str(len(filtered))))
            return filtered

        elif start_date and not end_date:
            print("{}: filtering through {} commits between start: {}, end: {}".format(self.github_repo_url.split('/')[-1], str(len(self.commits)), str(start_date), str(datetime.now())))
            filtered = list(filter(lambda c: norm_dt(c.committer_date) > start_date, self.commits))
            print("found {}\n".format(str(len(filtered))))
            return filtered
        elif not start_date and end_date:
            print("{}: filtering through {} commits between start: {}, end: {}".format(self.github_repo_url.split('/')[-1], str(len(self.commits)), str(self.commits[0].committer_date), str(end_date)))
            filtered = list(filter(lambda c: norm_dt(c.committer_date) < end_date, self.commits))
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
        print("{} most common commit messages for {} are:\n".format(n, self.github_repo_url))
        print(*list(Counter(commit_messages).most_common(n)), sep="\n")
        
