from datetime import datetime, date, timedelta
import json
from typing import Optional

from src import setup_data

REPOS_FILE = 'repos.json'
DAILY_REPORTS_PATH = 'reports/daily/'

def generate_daily_report(day: Optional[datetime]):
    with open(f"src/config/{REPOS_FILE}", "r") as f:
        tokens = json.load(f)
    
    if day:
        # generate report for datetime passed in 
        start_date = day
        end_date = datetime.combine(start_date + timedelta(days=1), datetime.min.time())
    else:
        # otherwise, default to today
        today = datetime.combine(date.today(), datetime.min.time())
        yesterday = datetime.combine(date.today() - timedelta(days=1), datetime.min.time())
        start_date = yesterday
        end_date = today

    daily_commits_data = {}
    for token_name, token_data in tokens.items():
        token_repos = token_data['repos']
        if len(token_repos) == 0:
            continue
        
        # get daily commits
        project_commits = setup_data.get_list_of_project_commits(token_repos, start_date=start_date, end_date=end_date)

        def create_commit_url(commit, token_repos):
            git_org = token_repos[0].split('/')[3]
            return f"https://github.com/{git_org}/{commit.project_name}/commit/{commit.hash}"

        # populate daily report
        daily_commits_data[token_name] = {
            "commit_count": len(project_commits),
            "lines_of_code": sum([c.lines for c in project_commits]),
            "commit_messages": [c.msg for c in project_commits],
            "distinct_authors": list(set([c.committer.name for c in project_commits])),
            "commit_urls": [create_commit_url(c, token_repos) for c in project_commits]
        }

    with open(f'{DAILY_REPORTS_PATH}{start_date.strftime("%Y-%m-%d")}.json', 'w', encoding='utf-8') as f:
        json.dump(daily_commits_data, f, ensure_ascii=False, indent=2)



def get_top_most_active(daily_json_path, n=10):
    """Sorts tokens by most active to least active

    Args:
        daily_json_path ([type]): [description]
        n ([type]): [the top n to add to the list]

    Returns:
        [List[tuple(token_name, commit_count)], List[tuple(token_name, lines_of_code)]]: two lists containing tuples of (token name, metric)
    """
    with open(daily_json_path, "r") as f:
        daily_report = json.load(f)
    
    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    daily_report__by_commits_as_list = [(token_name, int(token_data['commit_count'])) for token_name, token_data in daily_report.items()]
    sorted_by_commit_count = sorted(daily_report__by_commits_as_list, key=lambda x: x[1], reverse=True)

    daily_report__by_LOC_as_list = [(token_name, int(token_data['lines_of_code'])) for token_name, token_data in daily_report.items()]
    sorted_by_lines_of_code = sorted(daily_report__by_LOC_as_list, key=lambda x: x[1], reverse=True)

    return sorted_by_commit_count[:n], sorted_by_lines_of_code[:n]

if __name__ == "__main__":

    # generates the daily report, defaults to today if no datetime passed in
    generate_daily_report(datetime(year=2022, month=1, day=24))

    date_wanted = '2022-01-24'
    by_commits, by_LOC = get_top_most_active(f"{DAILY_REPORTS_PATH}{date_wanted}.json", n=10)
    print("Top projects by # of commits", *by_commits, sep="\n")
    print("Top projects by new lines of code", *by_LOC, sep="\n")
