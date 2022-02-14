from pydriller import Repository
from datetime import datetime

if __name__ == "__main__":
    
    for commit in Repository('https://github.com/Loopring/loopring-explorer', since=datetime(2022, 2, 11)).traverse_commits():
        print(
        'hash: {}\ncommit msg: {}\ncommitter_date: {}\ninsertions: {}\ndeletions: {}\n modified_files: {}\n\n\n'.format(commit.hash, commit.msg, commit.committer_date, commit.insertions, commit.deletions, commit.modified_files)
        )
        