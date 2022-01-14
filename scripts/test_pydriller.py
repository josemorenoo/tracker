from pydriller import Repository

if __name__ == "__main__":
    
    for commit in Repository('https://github.com/Loopring/loopring-web-v2').traverse_commits():
        print(
        'commit author:{}\n{}\n{}\n{}\n{}\n{}\n\n\n'.format(commit.msg, commit.committer_date, commit.insertions, commit.deletions, commit.dmm_unit_complexity, commit.dmm_unit_interfacing)
        )
        