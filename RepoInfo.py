from pydriller import Repository

from datetime import datetime
import pytz
from typing import Any, List

class RepoInfo:

    def __init__(self, githubRepoUrl: str):
        self.githubRepoUrl = githubRepoUrl
        self.commits = [commit for commit in Repository(self.githubRepoUrl).traverse_commits()]

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

    def _round_single_commit_by_time(self, commit, interval = 5):
        """
        takes a commit time and rounds it to the nearest 5 minutes so we can align it with the 5min crypto prices, 
        stores back in commit object
        """
        dt = commit.committer_date
        rounded_to_nearest_5min = int(interval * round(dt.minute / interval))
        commit.rounded_commit_time = datetime(dt.year, dt.month, dt.day, dt.hour, rounded_to_nearest_5min if rounded_to_nearest_5min != 60 else 0)
        return commit

    def round_commits(self, commits):
        return [self._round_single_commit_by_time(c) for c in commits]
        
