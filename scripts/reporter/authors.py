from datetime import datetime
import json
from tqdm import tqdm

from pydriller import Repository
from config.config_util import get_repos

DEV_JSON = 'reports/devs.json'

def get_authors_from_repo(repo: str):
    authors = set([commit.author.name for commit in Repository(repo, since=datetime(2021, 3, 1)).traverse_commits()])
    return list(authors)

def generate_authors_report():
    token_authors_dict = {}

    for token, metadata in tqdm(get_repos().items()):
        repo = metadata['repos']
        repo_authors = get_authors_from_repo(repo)

        if token in token_authors_dict:
            token_authors_dict[token]['authors'].extend(repo_authors),
            token_authors_dict[token]['num_authors'] += len(repo_authors)
        else:
            token_authors_dict[token] = {
                'authors': repo_authors,
                'num_authors': len(repo_authors)
            }
    
    with open(DEV_JSON, 'w') as f:
        json.dump(token_authors_dict, f, indent=2)

def add_token_to_authors_report(token):
    with open(DEV_JSON, 'r') as f:
        authors_report_dict = json.load(f)

    token_metdata = get_repos()[token]
    repos = token_metdata['repos']
    for repo in repos:
        repo_authors = get_authors_from_repo(repo)
        num_authors = len(repo_authors)

        if token in authors_report_dict:
            authors_report_dict[token]['authors'].extend(repo_authors),
            authors_report_dict[token]['num_authors'] += num_authors
            print(f"Added {num_authors} additional authors for {token}")
        else:
            authors_report_dict[token] = {
                'authors': repo_authors,
                'num_authors': num_authors
            }
            print(f"Added {num_authors} existing authors for {token}")
    with open(DEV_JSON, 'w') as f:
        json.dump(authors_report_dict, f, indent=2)


def get_all_authors_count(token):
    with open(DEV_JSON, 'r') as f:
        authors_report = json.load(f)
    token_authors = authors_report[token]
    return token_authors['num_authors']


if __name__ == "__main__":
    #generate_authors_report()
    add_token_to_authors_report('CKB')
