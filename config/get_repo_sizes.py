import json
import requests
from tqdm import tqdm

headers = {'Authorization': 'token ' + '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'}

repos = json.load(open('repos.json'))
repo_urls = []
for y in repos.values():
    repo_urls += y['repos']

with open('repo_sizes.txt', 'w') as f:
    for url in tqdm(repo_urls):
        api_endpoint = url.replace('github.com/', 'api.github.com/repos/')
        response = requests.get(api_endpoint, headers=headers).json()
        if 'size' in response:
            size_gb = round(int(response['size']) / 1000000,2)
            f.write(f"size: {size_gb}GB\t{url}\n")
        else:
            f.write(f"ERROR: {url}\t{response}\n\n")
    
