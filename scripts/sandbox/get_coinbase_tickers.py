
import requests
import json
import pandas as pd
import os

response = requests.get("https://api.pro.coinbase.com/products")
if response.status_code in [200, 201, 202, 203, 204]:
    response_data = pd.json_normalize(json.loads(response.text))

pairs_available = response_data['id']

tickers = []
for pair in pairs_available:
    a, b = pair.split('-')
    tickers.append(a); tickers.append(b)
tickers = set(tickers)

print(f"{len(tickers)} tickers available")
print(*tickers, sep="\n")

output_file = 'scripts/sandbox/output/tickers_available_on_coinbase.txt'
print(f'writing tickers to {output_file}')
os.system(f'touch {output_file}')
with open(output_file, 'w') as f:
    for ticker in tickers:
        f.write(ticker + '\n')