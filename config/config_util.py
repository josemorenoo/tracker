import json


def get_repos():
    with open(f"config/repos.json", "r") as f:
        repos = json.load(f)
    return repos