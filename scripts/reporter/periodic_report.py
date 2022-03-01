from collections import Counter
from datetime import datetime, date, timedelta
import json
import os
import time
from pandas import DataFrame
from tqdm import tqdm
from typing import Optional, List, Any

import config.config_util as config_util 
from scripts.reporter.paths import PATHS
import scripts.reporter.report_util as report_util

import scripts.twitter.twitter_graphs as graphs

from webapp import setup_data
from webapp.token_prices import CryptoOracle

def generate_weekly_report(start_date: datetime):
    start = time.time()
    with open(PATHS['REPOS_FILE'], "r") as f:
        tokens = json.load(f)

    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = start_date + timedelta(days=7)
    print(f"generating WEEKLY report, start: {start_date}, end: {end_date}")

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
            "commit_urls": [create_commit_url(c, token_repos) for c in project_commits],
            "file_extensions": report_util.get_file_extensions_and_lines_of_code_modified(project_commits),
            "changed_methods": list(set(report_util.get_changed_methods(project_commits)))
        }

    report_date_str = start_date.strftime("%Y-%m-%d")

    # create landing dir
    if not os.path.exists(f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}"):
        os.makedirs(f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}")

    # dump daily report
    with open(f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json", 'w', encoding='utf-8') as f:
        json.dump(weekly_commits_data, f, ensure_ascii=False, indent=2)

    end = time.time()
    duration = end-start
    print(f"~~~ {report_date_str} daily report generated in {str(timedelta(seconds=duration))}~~~")

def generate_daily_report(day: Optional[datetime]):
    start = time.time()
    with open(f"{PATHS['REPOS_FILE']}", "r") as f:
        tokens = json.load(f)
    
    if day:
        # generate report for datetime passed in 
        end_date = day
        start_date = datetime.combine(end_date - timedelta(hours=24), datetime.min.time())
        print(f"generating DAILY report, start: {start_date}, end: {end_date}")
    else:
        # otherwise, default to today
        today = datetime.combine(date.today(), datetime.min.time())
        yesterday = datetime.combine(date.today() - timedelta(hours=24), datetime.min.time())
        start_date = yesterday
        end_date = today
        print(f"generating DAILY report, start: {start_date}, end: {end_date}")

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
            "commit_urls": [create_commit_url(c, token_repos) for c in project_commits],
            "file_extensions": report_util.get_file_extensions_and_lines_of_code_modified(project_commits),
            "changed_methods": list(set(report_util.get_changed_methods(project_commits)))
        }

    report_date_str = day.strftime("%Y-%m-%d")

    # create landing dir
    if not os.path.exists(f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}"):
        os.makedirs(f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}")

    # dump daily report
    with open(f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json", 'w', encoding='utf-8') as f:
        json.dump(daily_commits_data, f, ensure_ascii=False, indent=2)

    end = time.time()
    duration = end-start
    print(f"~~~ {report_date_str} daily report generated in {str(timedelta(seconds=duration))}~~~")


def generate_summary_report(report_date, mode="DAILY"):
    """Displays the top 10 projects across multiple categories
    - most commits
    - most new lines of code
    - most distinct authors

    Assumes the daily report already exists at reports/daily/<YYY-MM-DD>/<YYY-MM-DD>.json

    Args:
        report_date_str (str): "YYY-MM-DD"
    """
    if mode=="DAILY":
        end_of_date = report_date + timedelta(hours=24)
        report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="WEEKLY":
        end_of_date = report_date + timedelta(days = 7)
        report_date_str = report_date.strftime("%Y-%m-%d")
   


    # display the top 10 from the daily report
    by_commits = report_util.get_most_active_by_commits(report_date_str, n=10, mode=mode)
    by_LOC = report_util.get_most_active_by_loc(report_date_str, n=10, mode=mode)
    by_distinct_authors = report_util.get_most_active_by_author(report_date_str, n=10, mode=mode)

    summary_report = {"tokens_represented": {}}

    # now get the open/close price for each token in report
    tokens_represented = set([x[0] for x in by_commits] + [x[0] for x in by_LOC] + [x[0] for x in by_distinct_authors])
    for token in tokens_represented:
        co = CryptoOracle(token)

        token_price_df = co.get_token_price_df(report_date, end_of_date, interval_sec=6*60*60)
        if len(token_price_df.index): # not empty
        
            # add price data for each token in top 10 across all categories
            daily_df = token_price_df.loc[[report_date_str]]
            open_price = daily_df['Open'].values[0], #token_price_df["Open"][0],
            close_price = daily_df['Close'].values[0], #token_price_df["Close"][-1]
            delta_percentage = round(100 * (close_price[0] - open_price[0]) / open_price[0], 2)

            if mode=="DAILY":
                summary_report["tokens_represented"][token] = {
                    "daily_open": open_price[0], # unpack single value tuple
                    "daily_close": close_price[0],
                    "delta_percentage": delta_percentage
                }
            if mode=="WEEKLY":
                summary_report["tokens_represented"][token] = {
                    "weekly_open": open_price[0], # unpack single value tuple
                    "weekly_close": close_price[0],
                    "delta_percentage": delta_percentage
                }
        else:
            if mode=="DAILY":
                summary_report["tokens_represented"][token] = {
                    "daily_open": None,
                    "daily_close": None,
                    "delta_percentage": None
                }
            if mode=="WEEKLY":
                summary_report["tokens_represented"][token] = {
                    "weekly_open": None,
                    "weekly_close": None,
                    "delta_percentage": None
                }


    summary_report["top_by_num_commits"] = [{"token": token, "count": count} for token, count in by_commits]
    summary_report["top_by_new_lines"] = [{"token": token, "count": count} for token, count in by_LOC]
    summary_report["top_by_num_distinct_authors"] = [{"token": token, "count": count} for token, count in by_distinct_authors]

    # generate file extension breakdown for all tokens represented
    tokens_represented = summary_report["tokens_represented"].keys()
    graphs.create_file_extension_base_img(tokens_represented, report_date, mode)

    if mode=="DAILY":
        with open(f'{PATHS["DAILY_REPORTS_PATH"]}/{report_date_str}/summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)
    if mode=="WEEKLY":
        with open(f'{PATHS["WEEKLY_REPORTS_PATH"]}/{report_date_str}/summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)


def run(report_date, mode="DAILY", make_raw_report:bool=True, make_summary_report=True):
    if make_raw_report: 
        if mode=="DAILY":
            generate_daily_report(report_date)
        if mode=="WEEKLY":
            generate_weekly_report(report_date)

    if make_summary_report:
        # generate summary report, used by twitter graphs
        generate_summary_report(report_date, mode)


if __name__ == "__main__":
    run()
    
