from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

from time_util import datetime_to_ms_timestamp, round_single_commit_by_time

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
    ms_timestamp: int
    committer_timezone: int
    in_main_branch: bool
    merge: bool
    modified_files: List[Any]
    project_name: str
    deletions: int
    insertions: int
    lines: int
    files: int
    dmm_unit_size: float
    dmm_unit_complexity: float
    dmm_unit_interfacing: float
    rounded_commit_time_5min: str # custom

class CommitHandler:

    def create_commit(self, commit):
        '''
        Takes in a raw pydriller commit object and extracts the relevant fields into a new
        Commit dataclass object
        '''
        print(" loading commit from {}".format(commit.project_name))
        return Commit(
            msg = commit.msg,
            author = commit.author ,
            committer = commit.committer,
            author_date = commit.author_date,
            author_timezone = commit.author_timezone,
            committer_date = commit.committer_date,
            ms_timestamp = datetime_to_ms_timestamp(commit.committer_date),
            committer_timezone = commit.committer_timezone,
            in_main_branch = commit.in_main_branch,
            merge = commit.merge,
            modified_files = commit.modified_files,
            project_name = commit.project_name,
            deletions = commit.deletions,
            insertions = commit.insertions,
            lines = commit.lines,
            files = commit.files,
            dmm_unit_size = commit.dmm_unit_size,
            dmm_unit_complexity = commit.dmm_unit_complexity,
            dmm_unit_interfacing = commit.dmm_unit_interfacing,
            rounded_commit_time_5min = round_single_commit_by_time(commit.committer_date, granularity_min = 5)
        )

        
        

