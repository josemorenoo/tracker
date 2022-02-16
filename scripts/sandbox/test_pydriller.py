from pydriller import Repository
from datetime import datetime

if __name__ == "__main__":
    
    for commit in Repository('https://github.com/Loopring/loopring-explorer', since=datetime(2022, 2, 11)).traverse_commits():
        print('msg: ', commit.msg)
        print('insertions: ', commit.insertions)
        print(*[f.filename for f in commit.modified_files], sep="\n")
        print('\n\n')
        