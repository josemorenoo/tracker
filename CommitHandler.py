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

class CommitHandler:
    def create_commit(commit):
        '''
        Takes in a raw pydriller commit object and extracts the relevant fields into a new
        Commit dataclass object
        '''
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
            dmm_unit_interfacing = commit.dmm_unit_interfacing
        )
        

