import json
from typing import Any, List

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

    # sort in descending order, [(token_name, commit_count or lines_of_code), ...]
    sort_by_metric = lambda report_list: sorted(report_list, key=lambda x: x[1], reverse=True)
    report_by_most_authors = [(token_name, int(len(token_data['distinct_authors']))) for token_name, token_data in report.items()]
    by_distinct_authors = sort_by_metric(report_by_most_authors)[:n]
    print("\nTop projects by distinct authors", *by_distinct_authors, sep="\n")
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

def get_file_extensions_by_token(report_date_str: str, mode="DAILY"):
    """
    For tokens represented in the report, return a list of file extensions that were modified
    """
    if mode=="DAILY":
        report_json_path = f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"
    elif mode=="WEEKLY":
        report_json_path = f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json"

    with open(report_json_path, "r") as f:
        report = json.load(f)

    file_extensions_by_token = {token_name: token_data['file_extensions'] for token_name, token_data in report.items()}
    return file_extensions_by_token

### ### ### ### ### ### vvv PRICE vvv ### ### ### ### ### ### 

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


### ### ### ### ### ### vvv MISCELLANEOUS vvv
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


def get_commit_message_word_list(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")

    if mode=="DAILY":
        with open(f"{PATHS['DAILY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json", 'r') as f:
            report = json.load(f)
    if mode=="WEEKLY":
        with open(f"{PATHS['WEEKLY_REPORTS_PATH']}/{report_date_str}/{report_date_str}.json", 'r') as f:
            report = json.load(f)


    commit_messages_as_list_of_words = []
    for _, token_data in report.items():
        commit_messages_as_list_of_words.extend([msg.split(' ') for msg in token_data['commit_messages']])
    
    word_list = []
    for sublist in commit_messages_as_list_of_words:
        word_list.extend(sublist)
    print(word_list)
    return word_list