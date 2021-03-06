from collections import Counter, defaultdict
from datetime import timedelta
import json
from typing import Any, List

from assets.file_extension_imgs.file_extensions import FILE_EXTENSIONS
from scripts.reporter.authors import get_all_authors_count
from scripts.reporter.paths import PATHS

### ### ### ### ### vvv METRICS vvv ### ### ### ### ### 

def get_most_active_by_commits(report_date_str: str, n=10, mode="DAILY"):
    """Sorts tokens by most active to least active

    Args:
        report_date_str ([type]): [YYYY-MM-DD]
        n ([type]): [the top n to add to the list]

    Returns:
        [List[tuple(token_name, commit_count)]
    """
    if mode=="DAILY":
        report_json_path = f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"
    elif mode=="WEEKLY":
        report_json_path = f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"

    with open(report_json_path, "r") as f:
        report = json.load(f)

    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    sort_by_metric = lambda report_list: sorted(report_list, key=lambda x: x[1], reverse=True)
    report_by_most_commits_as_list = [(token_name, int(token_data['commit_count'])) for token_name, token_data in report.items()]
    by_commits =  sort_by_metric(report_by_most_commits_as_list)[:n]
    print("\nTop projects by # of commits", *by_commits, sep="\n")
    return by_commits

def get_most_active_by_author(report_date_str: str, n=10, mode="DAILY"):
    """Sorts tokens by most active to least active

    Args:
        report_date_str ([type]): [YYYY-MM-DD]
        n ([type]): [the top n to add to the list]

    Returns:
        [List[tuple(token_name, commit_count)]
    """
    if mode=="DAILY":
        report_json_path = f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"
    elif mode=="WEEKLY":
        report_json_path = f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"

    with open(report_json_path, "r") as f:
        report = json.load(f)

    def _get_all_authors_count(token): 
        c = get_all_authors_count(token)
        if c == 0:
            return None
        else:
            return c  

    def get_active_dev_ratio(token_name, token_data):
        if _get_all_authors_count(token_name):
            ratio = float(len(token_data['distinct_authors'])) / _get_all_authors_count(token_name)
            return ratio
        else:
            return None


    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    sort_by_metric = lambda report_list: sorted(report_list, key=lambda x: x[2], reverse=True)
    get_num_authors = lambda token_data: int(len(token_data['distinct_authors']))

    report_by_most_authors = [(
        token_name,
        get_num_authors(token_data),
        get_active_dev_ratio(token_name, token_data),
        f'{get_num_authors(token_data)}/{_get_all_authors_count(token_name)} devs'
    ) for token_name, token_data in report.items() if get_active_dev_ratio(token_name, token_data) and _get_all_authors_count(token_name) > 1]
    by_distinct_authors = sort_by_metric(report_by_most_authors)[:n]
 
    return by_distinct_authors

def get_most_active_by_loc(report_date_str: str, n=10, mode="DAILY"):
    """Sorts tokens by most active to least active

    Args:
        report_date_str ([type]): [YYYY-MM-DD]
        n ([type]): [the top n to add to the list]

    Returns:
        [List[tuple(token_name, commit_count)]
    """
    if mode=="DAILY":
        report_json_path = f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"
    elif mode=="WEEKLY":
        report_json_path = f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"

    with open(report_json_path, "r") as f:
        report = json.load(f)

    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    sort_by_metric = lambda report_list: sorted(report_list, key=lambda x: x[1], reverse=True)
    report_by_most_LOC_list = [(token_name, int(token_data['lines_of_code'])) for token_name, token_data in report.items()]
    by_LOC = sort_by_metric(report_by_most_LOC_list)[:n]
    print("\nTop projects by new lines of code", *by_LOC, sep="\n")
    return by_LOC


def get_file_extensions_and_lines_of_code_modified(project_commits):
    """
    USED TO POPULATE THE DAILY/WEEKLY REPORT

    For a single token, 

    returns a count of how many times each file type shows up,
    and a count of how many files were affected by each respective file extension

    ABC: {
        json: {extension_count: 4, loc_modified: 233},
        py: {extension_count: 3, loc_modified: -4}
    }
    """
    

    project_ext_count_and_loc_affected = {}  
    for commit in project_commits:

        # count how many times each file extension was modified for this token
        for ext, commit_ext_count in Counter(commit.file_extensions).items():
            if ext not in project_ext_count_and_loc_affected:
                project_ext_count_and_loc_affected[ext] = {'extension_count': commit_ext_count}
            else:
                project_ext_count_and_loc_affected[ext]['extension_count'] += commit_ext_count

            # log out if extension is new so we can add a picture of it
            if ext not in FILE_EXTENSIONS:
                print(f"NEW EXTENSIONS ALERT: {ext}")

        # count the number of lines of code affected for each respective file extension
        for ext, loc_modified_for_extension in commit.loc_changed_by_file_extension.items():
            project_ext_count_and_loc_affected[ext]['loc_modified'] = loc_modified_for_extension

    return project_ext_count_and_loc_affected


def get_file_extension_breakdown_from_summary_report(token, report_date, mode="DAILY", verbose=False):
    """
    PULLS FROM DAILY/WEEKLY REPORT

    for a single token,

    return a dict of file extensions that were modified, and their count, as well as the number of files affected

    # sort by number of file extensions updated
    """
    raw_report = get_raw_report(report_date=report_date, mode=mode) # raw means daily/weekly

    def combine_dicts(d1, d2):
        return dict(list(d1.items()) + list(d2.items()))
    token_specific_extension_data = [combine_dicts({'extension': extension}, metadata) for extension, metadata in raw_report[token]['file_extensions'].items()]

    sorted_by_extension_count = sorted(
        token_specific_extension_data,
        key=lambda x: x['extension_count'], 
        reverse=True)
    if verbose:
        print(f"Most popular file extensions for {token}")
        print(*sorted_by_extension_count, sep="\n")
    return sorted_by_extension_count

def get_changed_methods(project_commits) -> List[str]:
    """
    Used to populate the DAILY/WEEKLY reports, gets a list of 
    method names that were changed.

    Note: Removes duplicates from list, sometimes same method is touched in more than one commit
    """
    project_changed_methods = []
    for commit in project_commits:
        for file in commit.modified_files:
            method_names = [m.name for m in file.changed_methods]
            project_changed_methods.extend(method_names)
    print(*project_changed_methods, sep="\n")
    return list(set(project_changed_methods))


### ### ### ### ### ### vvv PRICE vvv ### ### ### ### ### ### 

def get_daily_price_deltas(sorted_tokens: List[Any], report_date, mode="DAILY"):
    summary_report = get_summary_report(report_date, mode)
    return [summary_report["tokens_represented"][token]["delta_percentage"] for token in sorted_tokens]

### ### ### ### ### ### vvv REPORTS vvv
# 
#  ### ### ### ### ### ### 
def get_summary_report(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        with open(f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/summary.json", 'r') as f:
            summary_report = json.load(f)
    if mode=="WEEKLY":
        with open(f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/summary.json", 'r') as f:
            summary_report = json.load(f)
    return summary_report

def get_raw_report(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        with open(f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json", 'r') as f:
            raw_report = json.load(f)
    if mode=="WEEKLY":
        with open(f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json", 'r') as f:
            raw_report = json.load(f)
    return raw_report
