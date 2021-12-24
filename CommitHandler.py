from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

@dataclass
class Commit:
    """
    This is just a dataclass that holds data, see class below

    You can then do something like 
    c = Commit('hello ', 'nini', ...)
    print(c.msg + c.author)
    >>> 'hello nini'
    """
    msg: str
    author: str
    committer: str
    author_date: datetime
    author_timezone: int
    committer_date: datetime
    committer_timezone: int
    in_main_branch: bool
    merge: bool
    modified_files: List[Any]
    project_name: str
    project_path: str
    deletions: int
    insertions: int
    lines: int
    files: int
    dmm_unit_size: float
    dmm_unit_complexity: float
    dmm_unit_interfacing: float
    rounded_commit_time_5min: str # custom

class CommitHandler:

    def _round_single_commit_by_time(self, commit, interval = 5):
        """
        Takes a commit time and rounds it to the nearest 5 minutes so we can align it with the 5min crypto prices
        """
        dt = commit.committer_date
        nearest_5min = int(interval * round(dt.minute / interval))
        rounded_commit_time = datetime(dt.year, dt.month, dt.day, dt.hour, nearest_5min if nearest_5min != 60 else 0)
        return rounded_commit_time

    def create_commit(self, commit):
        '''
        Takes in a raw pydriller commit object and extracts the relevant fields into a new
        Commit dataclass object
        '''
        print(" loading commit")
        return Commit(
            msg = commit.msg,
            author = commit.author ,
            committer = commit.committer,
            author_date = commit.author_date,
            author_timezone = commit.author_timezone,
            committer_date = commit.committer_date,
            committer_timezone = commit.committer_timezone,
            in_main_branch = commit.in_main_branch,
            merge = commit.merge,
            modified_files = commit.modified_files,
            project_name = commit.project_name,
            project_path = commit.project_path,
            deletions = commit.deletions,
            insertions = commit.insertions,
            lines = commit.lines,
            files = commit.files,
            dmm_unit_size = commit.dmm_unit_size,
            dmm_unit_complexity = commit.dmm_unit_complexity,
            dmm_unit_interfacing = commit.dmm_unit_interfacing,
            rounded_commit_time_5min = self._round_single_commit_by_time(commit, interval = 5)
        )

        
        

