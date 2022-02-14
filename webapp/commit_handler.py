from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from .time_util import datetime_to_ms_timestamp, round_single_commit_by_time

# files we don't want to count towards lines of code
EXCLUSION_LIST = [
    'yarn.lock',
    'package.json'
]

@dataclass
class Commit:
    """
    This is just a dataclass that holds data, see class below

    You can then do something like 
    c = Commit('hello ', 'nini', ...)
    print(c.msg + c.author)
    >>> 'hello nini'
    """
    hash: str
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
    project_path: str
    deletions: int
    insertions: int
    lines: int
    files: int
    dmm_unit_size: float
    dmm_unit_complexity: float
    dmm_unit_interfacing: float

    # non pydriller.Commit custom attributes below
    rounded_commit_time_5min: str
    file_extensions: List[str]
    loc_changed_by_file_extension: Dict[str, int]
    methods_modified: List[str] 

class CommitHandler:

    def create_commit(self, commit):
        '''
        Takes in a raw pydriller commit object and extracts the relevant fields into a new
        Commit dataclass object
        '''
        print(" loading commit from {}".format(commit.project_name))
        
        # lines is insertions AND deletions
        deletions, insertions, lines = commit.deletions, commit.insertions, commit.lines

        # if file is in exclusion list by extension, ignore for line count
        for modified_file in commit.modified_files:
            if modified_file.filename.endswith(tuple(EXCLUSION_LIST)):
                deletions -= modified_file.deleted_lines
                insertions -= modified_file.added_lines
                lines -= (modified_file.deleted_lines + modified_file.added_lines)

        return Commit(
            hash = commit.hash,
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
            project_path = commit.project_path,
            deletions = deletions,
            insertions = insertions,
            lines = lines,
            files = commit.files,
            dmm_unit_size = commit.dmm_unit_size,
            dmm_unit_complexity = commit.dmm_unit_complexity,
            dmm_unit_interfacing = commit.dmm_unit_interfacing,
            rounded_commit_time_5min = round_single_commit_by_time(commit.committer_date, granularity_min = 5),
            file_extensions = self.get_commit_file_extensions(commit),
            loc_changed_by_file_extension = self.get_loc_changed_by_file_extension(commit),
            methods_modified = self.get_methods_modified(commit)
        )

    def get_commit_file_extensions(self, commit) -> List[str]:
        """
        Returns a list of the file extensions of files changed in a single commit
        """
        return [f.filename.split('.')[-1] for f in commit.modified_files]

    def get_loc_changed_by_file_extension(self, commit) -> Dict[str, int]:
        """
        Returns a dictionary which counts the lines of code changed by all files with the same file extension in a single commit

        # example of single commit
        a.json +5
        aa.json +5
        aaa.json +5
        b.py +4
        c.js +90

        returns: 
        {json: 15, py: 4, js: 90}
        """
        tally_dictionary = defaultdict(int)
        for f in commit.modified_files:
            extension_name = f.filename.split('.')[-1]
            tally_dictionary[extension_name] += (f.added_lines - f.deleted_lines)
        return tally_dictionary

    def get_methods_modified(self, commit) -> List[str]:
        changed_methods_nested = [f.changed_methods for f in commit.modified_files]
        #unpack list of lists into single list
        return [item for sublist in changed_methods_nested for item in sublist]

