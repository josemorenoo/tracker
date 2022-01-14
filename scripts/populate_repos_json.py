import json
import os
code_root = os.getcwd()

repos_json = json.load(open(f'{code_root}/config/repos.json'))

with open(f'{code_root}/tickers_available_on_coinbase.txt', 'r') as f:
    tickers = f.readlines()

for ticker in tickers:
    ticker = ticker.replace('\n', '')
    repos_json[ticker] = {"name": "", "repos":[]}

with open(f'{code_root}/config/fresh_repos_template.json', 'w', encoding='utf-8') as f:
    json.dump(repos_json, f, ensure_ascii=False, indent=2)