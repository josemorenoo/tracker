from calendar import day_abbr
from datetime import datetime, date, timedelta
import json
import os
import time
from tqdm import tqdm
from typing import Optional, List, Any

from src import setup_data
from src.crypto_oracle import CryptoOracle

REPOS_FILE = 'repos.json'
DAILY_REPORTS_PATH = 'reports/daily'
WEEKLY_REPORTS_PATH = 'reports/weekly'

def generate_weekly_report(end_date: datetime):
    with open(f"src/config/{REPOS_FILE}", "r") as f:
        tokens = json.load(f)

    start_date = datetime.combine(end_date - timedelta(days=7), datetime.min.time())

    weekly_commits_data = {}
    for token_name, token_data in tqdm(tokens.items()):
        token_repos = token_data['repos']
        if len(token_repos) == 0:
            continue

        # get weekly commits
        project_commits = setup_data.get_list_of_project_commits(token_repos, start_date=start_date, end_date=end_date)

        def create_commit_url(commit, token_repos):
            git_org = token_repos[0].split('/')[3]
            return f"https://github.com/{git_org}/{commit.project_name}/commit/{commit.hash}"

        # populate daily report
        weekly_commits_data[token_name] = {
            "commit_count": len(project_commits),
            "lines_of_code": sum([c.insertions for c in project_commits]),
            "commit_messages": [c.msg for c in project_commits],
            "distinct_authors": list(set([c.committer.name for c in project_commits])),
            "commit_urls": [create_commit_url(c, token_repos) for c in project_commits]
        }

    report_date_str = end_date.strftime("%Y-%m-%d")

    # create landing dir
    if not os.path.exists(f"{WEEKLY_REPORTS_PATH}/{report_date_str}"):
        os.makedirs(f"{WEEKLY_REPORTS_PATH}/{report_date_str}")

    # dump daily report
    with open(f'{WEEKLY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json', 'w', encoding='utf-8') as f:
        json.dump(weekly_commits_data, f, ensure_ascii=False, indent=2)

def generate_daily_report(day: Optional[datetime]):
    with open(f"src/config/{REPOS_FILE}", "r") as f:
        tokens = json.load(f)
    
    if day:
        # generate report for datetime passed in 
        end_date = day
        start_date = datetime.combine(end_date - timedelta(hours=24), datetime.min.time())
        
    else:
        # otherwise, default to today
        today = datetime.combine(date.today(), datetime.min.time())
        yesterday = datetime.combine(date.today() - timedelta(hours=24), datetime.min.time())
        start_date = yesterday
        end_date = today

    daily_commits_data = {}
    for token_name, token_data in tqdm(tokens.items()):
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
            "lines_of_code": sum([c.insertions for c in project_commits]),
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

def get_top_most_active(report_date_str: str, n=10, mode="DAILY"):
    """Sorts tokens by most active to least active

    Args:
        report_date_str ([type]): [YYYY-MM-DD]
        n ([type]): [the top n to add to the list]

    Returns:
        [List[tuple(token_name, commit_count)], List[tuple(token_name, lines_of_code)]]: two lists containing tuples of (token name, metric)
    """
    if mode=="DAILY":
        report_json_path = f"{DAILY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json"
    elif mode=="WEEKLY":
        report_json_path = f"{WEEKLY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json"

    with open(report_json_path, "r") as f:
        report = json.load(f)
    
    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    sort_by_metric = lambda report_list: sorted(report_list, key=lambda x: x[1], reverse=True)

    daily_report_by_commits_as_list = [(token_name, int(token_data['commit_count'])) for token_name, token_data in report.items()]
    sorted_by_commit_count = sort_by_metric(daily_report_by_commits_as_list)

    daily_report_by_LOC_as_list = [(token_name, int(token_data['lines_of_code'])) for token_name, token_data in report.items()]
    sorted_by_lines_of_code = sort_by_metric(daily_report_by_LOC_as_list)

    daily_report_by_distinct_authors = [(token_name, int(len(token_data['distinct_authors']))) for token_name, token_data in report.items()]
    sorted_by_distinct_authors = sort_by_metric(daily_report_by_distinct_authors)

    return sorted_by_commit_count[:n], sorted_by_lines_of_code[:n], sorted_by_distinct_authors[:n]

def get_summary_report(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        with open(f'{DAILY_REPORTS_PATH}/{report_date_str}/summary.json', 'r') as f:
            summary_report = json.load(f)
    if mode=="WEEKLY":
        with open(f'{WEEKLY_REPORTS_PATH}/{report_date_str}/summary.json', 'r') as f:
            summary_report = json.load(f)
    return summary_report

def get_combined_price_deltas(sorted_tokens: List[Any], report_date, mode="DAILY"):
    price_deltas = get_daily_price_deltas([x[0] for x in sorted_tokens], report_date, mode)
    avg_delta = sum(price_deltas) / len(price_deltas)
    print(f"average cumulative return for {sorted_tokens} is {avg_delta} | {mode}")
    return avg_delta

def get_daily_price_deltas(sorted_tokens: List[Any], report_date, mode="DAILY"):
    summary_report = get_summary_report(report_date, mode)
    if mode=="DAILY":
        return [summary_report["tokens_represented"][token]["daily_delta_percentage"] for token in sorted_tokens]
    if mode=="WEEKLY":
        return [summary_report["tokens_represented"][token]["weekly_delta_percentage"] for token in sorted_tokens]

def generate_summary_report(report_date, mode="DAILY"):
    """Displays the top 10 projects across multiple categories
    - most commits
    - most new lines of code
    - most distinct authors

    Assumes the daily report already exists at reports/daily/<YYY-MM-DD>/<YYY-MM-DD>.json

    Args:
        report_date_str (str): "YYY-MM-DD"
    """
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        end_of_date = report_date + timedelta(hours=24)
    if mode=="WEEKLY":
        end_of_date = report_date
        report_date = end_of_date - timedelta(days = 7)


    # display the top 10 from the daily report
    by_commits, by_LOC, by_distinct_authors = get_top_most_active(report_date_str, n=10, mode=mode)
    print("\nTop projects by # of commits", *by_commits, sep="\n")
    print("\nTop projects by new lines of code", *by_LOC, sep="\n")
    print("\nTop projects by distinct authors", *by_distinct_authors, sep="\n")

    summary_report = {"tokens_represented": {}}

    # now get the open/close price for each token in report
    tokens_represented = set([x[0] for x in by_commits] + [x[0] for x in by_LOC] + [x[0] for x in by_distinct_authors])
    for token in tokens_represented:
        co = CryptoOracle(token)
        token_price_df = co.get_token_price_df(report_date, end_of_date, interval_sec=6*60*60)

        # add price data for each token in top 10 across all categories
        open_price = token_price_df["open"][0],
        close_price = token_price_df["close"][-1],
        delta_percentage = round(100 * (close_price[0] - open_price[0]) / open_price[0], 2)

        if mode=="DAILY":
            summary_report["tokens_represented"][token] = {
                "daily_open": open_price[0], # unpack single value tuple
                "daily_close": close_price[0],
                "daily_delta_percentage": delta_percentage
            }
        if mode=="WEEKLY":
            summary_report["tokens_represented"][token] = {
                "weekly_open": open_price[0], # unpack single value tuple
                "weekly_close": close_price[0],
                "weekly_delta_percentage": delta_percentage
            }

    summary_report["top_by_num_commits"] = [{"token": token, "count": count} for token, count in by_commits]
    summary_report["top_by_new_lines"] = [{"token": token, "count": count} for token, count in by_LOC]
    summary_report["top_by_num_distinct_authors"] = [{"token": token, "count": count} for token, count in by_distinct_authors]

    if mode=="DAILY":
        with open(f'{DAILY_REPORTS_PATH}/{report_date_str}/summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)
    if mode=="WEEKLY":
        with open(f'{WEEKLY_REPORTS_PATH}/{report_date_str}/summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)

def get_commit_message_word_list(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")

    if mode=="DAILY":
        with open(f'{DAILY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json', 'r') as f:
            report = json.load(f)
    if mode=="WEEKLY":
        with open(f'{WEEKLY_REPORTS_PATH}/{report_date_str}/{report_date_str}.json', 'r') as f:
            report = json.load(f)


    commit_messages_as_list_of_words = []
    for _, token_data in report.items():
        commit_messages_as_list_of_words.extend([msg.split(' ') for msg in token_data['commit_messages']])
    
    word_list = []
    for sublist in commit_messages_as_list_of_words:
        word_list.extend(sublist)
    print(word_list)
    return word_list


def run(report_date, mode="DAILY"):    
    if mode=="DAILY":
        generate_daily_report(report_date)
    if mode=="WEEKLY":
        generate_weekly_report(report_date)

    # generate summary report, used by twitter graphs
    generate_summary_report(report_date, mode)


if __name__ == "__main__":
    run()
    
