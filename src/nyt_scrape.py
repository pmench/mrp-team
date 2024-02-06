import pandas as pd

url = "https://www.nytimes.com/interactive/2023/12/19/us/elections/times-siena-poll-registered-voter-crosstabs.html"
nyt = pd.read_html(url)

for i, table in enumerate(nyt):
    table.to_csv(f"../data/nyt_table_{i}.csv", index=False)
