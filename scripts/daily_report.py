from datetime import datetime, date, timedelta
import json
import os
import time
from typing import Optional, List, Any

from src import setup_data
from src.crypto_oracle import CryptoOracle

REPOS_FILE = 'repos.json'
DAILY_REPORTS_PATH = 'reports/daily'

def generate_daily_report(day: Optional[datetime]):
    with open(f"src/config/{REPOS_FILE}", "r") as f:
        tokens = json.load(f)
    
    if day:
        # generate report for datetime passed in 
        end_date = day
        start_date = datetime.combine(end_date - timedelta(days=1), datetime.min.time())
        
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

    report_date_str = day.strftime("%Y-%m-%d")

    # create landing dir
    if not os.path.exists(f"{DAILY_REPORTS_PATH}/{report_date_str}"):
        os.makedirs(f"{DAILY_REPORTS_PATH}/{report_date_str}")

    # dump daily report
    with open(f'{DAILY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json', 'w', encoding='utf-8') as f:
        json.dump(daily_commits_data, f, ensure_ascii=False, indent=2)

def get_top_most_active(report_date_str: str, n=10):
    """Sorts tokens by most active to least active

    Args:
        report_date_str ([type]): [YYYY-MM-DD]
        n ([type]): [the top n to add to the list]

    Returns:
        [List[tuple(token_name, commit_count)], List[tuple(token_name, lines_of_code)]]: two lists containing tuples of (token name, metric)
    """
    daily_json_path = f"{DAILY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json"

    with open(daily_json_path, "r") as f:
        daily_report = json.load(f)
    
    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    sort_by_metric = lambda report_list: sorted(report_list, key=lambda x: x[1], reverse=True)

    daily_report_by_commits_as_list = [(token_name, int(token_data['commit_count'])) for token_name, token_data in daily_report.items()]
    sorted_by_commit_count = sort_by_metric(daily_report_by_commits_as_list)

    daily_report_by_LOC_as_list = [(token_name, int(token_data['lines_of_code'])) for token_name, token_data in daily_report.items()]
    sorted_by_lines_of_code = sort_by_metric(daily_report_by_LOC_as_list)

    daily_report_by_distinct_authors = [(token_name, int(len(token_data['distinct_authors']))) for token_name, token_data in daily_report.items()]
    sorted_by_distinct_authors = sort_by_metric(daily_report_by_distinct_authors)

    return sorted_by_commit_count[:n], sorted_by_lines_of_code[:n], sorted_by_distinct_authors[:n]

def get_daily_price_deltas(sorted_tokens: List[Any], report_date_str):
    with open(f'{DAILY_REPORTS_PATH}/{report_date_str}/summary.json', 'r') as f:
        summary_report = json.load(f)
    return [summary_report["tokens_represented"][token]["daily_delta_percentage"] for token in sorted_tokens]

def generate_summary_report(report_date):
    """Displays the top 10 projects across multiple categories
    - most commits
    - most new lines of code
    - most distinct authors

    Assumes the daily report already exists at reports/daily/<YYY-MM-DD>/<YYY-MM-DD>.json

    Args:
        report_date_str (str): "YYY-MM-DD"
    """
    report_date_str = report_date.strftime("%Y-%m-%d")
    end_of_date = report_date + timedelta(days=1)

    # display the top 10 from the daily report
    by_commits, by_LOC, by_distinct_authors = get_top_most_active(report_date_str, n=10)
    print("\nTop projects by # of commits", *by_commits, sep="\n")
    print("\nTop projects by new lines of code", *by_LOC, sep="\n")
    print("\nTop projects by distinct authors", *by_distinct_authors, sep="\n")

    summary_report = {"tokens_represented": {}}

    # now get the daily open/close price for each token in report
    tokens_represented = set([x[0] for x in by_commits] + [x[0] for x in by_LOC] + [x[0] for x in by_distinct_authors])
    for token in tokens_represented:
        co = CryptoOracle(token)
        token_price_df = co.get_token_price_df(report_date, end_of_date, interval_sec=6*60*60)

        # add price data for each token in top 10 across all categories
        daily_open = token_price_df["open"][0],
        daily_close = token_price_df["close"][-1],
        daily_delta_percentage = round(100 * (daily_close[0] - daily_open[0]) / daily_open[0], 2)

        summary_report["tokens_represented"][token] = {
            "daily_open": daily_open[0], # unpack single value tuple
            "daily_close": daily_close[0],
            "daily_delta_percentage": daily_delta_percentage
        }

    summary_report["top_by_num_commits"] = [{"token": token, "count": count} for token, count in by_commits]
    summary_report["top_by_new_lines"] = [{"token": token, "count": count} for token, count in by_LOC]
    summary_report["top_by_num_distinct_authors"] = [{"token": token, "count": count} for token, count in by_distinct_authors]

    with open(f'{DAILY_REPORTS_PATH}/{report_date_str}/summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, ensure_ascii=False, indent=2)

def run():
    today = datetime.today()
    
    # generate the daily report
    generate_daily_report(today)

    # generate summary report, used by twitter graphs
    generate_summary_report(today)


if __name__ == "__main__":
    run()
    
