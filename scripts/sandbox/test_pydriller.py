from pathlib import Path
from pydriller import Repository, Git
from datetime import datetime, time
import tempfile

from webapp.commit_handler import CommitHandler

def commit_test():
    for commit in Repository('https://github.com/Loopring/loopring-explorer', since=datetime(2022, 2, 11)).traverse_commits():
        print(f"got one: {commit.hash}, {commit.msg}")

        ch = CommitHandler()

        tmp_dir = tempfile.TemporaryDirectory()
        tmp_dir_path = Path(tmp_dir.name)
        tmp_dir_path.mkdir(parents=True, exist_ok=True)
        tmp_dir_str = str(tmp_dir_path.resolve())

        ch.create_commit(commit, tmp_dir_str)
        tmp_dir.cleanup()

if __name__ == "__main__":
    authors = []
    for commit in Repository('https://github.com/Loopring/loopring-explorer', since=datetime(2021, 3, 1)).traverse_commits():
        authors.append(commit.author.name)
    print(set(authors))

        
    

        