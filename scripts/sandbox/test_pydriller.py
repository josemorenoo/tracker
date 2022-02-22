from pathlib import Path
from pydriller import Repository
from datetime import datetime
import tempfile

from webapp.commit_handler import CommitHandler


if __name__ == "__main__":
    
    for commit in Repository('https://github.com/Loopring/loopring-explorer', since=datetime(2022, 2, 11)).traverse_commits():
        print(f"got one: {commit.hash}, {commit.msg}")

        ch = CommitHandler()

        tmp_dir = tempfile.TemporaryDirectory()
        tmp_dir_path = Path(tmp_dir.name)
        tmp_dir_path.mkdir(parents=True, exist_ok=True)
        tmp_dir_str = str(tmp_dir_path.resolve())

        ch.create_commit(commit, tmp_dir_str)
        tmp_dir.cleanup()

        