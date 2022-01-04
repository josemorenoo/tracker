# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


from setup import load_data
from Stats import Stats
#from HairyPlotter import HairyPlotter


if __name__ == "__main__":
    # setup
    read_from_pickle = True
    token="LRC"
    start_date = datetime(2021, 11, 1, 12, 00, 00)
    end_date = datetime(2021, 12, 1, 12, 00, 00)
    timeframe = "month"

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]

    token_data_df, project_commits_list = load_data(
        token,
        project_repos,
        start_date,
        end_date,
        pickle_data_interval = timeframe, # see data/*/x_commits.pickle for value to put here
        read_from_pickle = read_from_pickle,
        write_to_pickle = not read_from_pickle
    )

    # create dash instance
    dash_app = dash.Dash(__name__)
    
    # add price plot
    fig = px.line(token_data_df, x='ms_timestamp', y="close", title=f"Commit Count vs {token} Price")
    fig.layout.update(yaxis = go.YAxis(title=f"{token} price in USD", side="left"))
    
    # add commits over price plot
    ts_bucket_list, commits_per_bucket = Stats.calculate_commit_count_in_range(project_commits_list, "5min")
    commits_df = pd.DataFrame({
        'ms_timestamp': ts_bucket_list,
        'commits_per_5min_range': commits_per_bucket 
    })

    # add number of commits for each 5min window
    fig.add_trace(go.Scatter(
        mode="markers",
        x=commits_df["ms_timestamp"],
        y=commits_df["commits_per_5min_range"],
        name="Total # Commits",
        yaxis='y2'))
    fig.layout.update(yaxis2 = go.YAxis(title="Total # Commits", overlaying='y', side='right'))

    # create the dashboard page
    dash_app.layout = html.Div([
        dcc.Graph(
            id='price-vs-some-metric',
            figure=fig
        )
    ])

    # this needs to run last AFTER you configure the dash_app object layout
    dash_app.run_server(debug=True)

    """
    # matplotlib
    hp = HairyPlotter()
    hp.show_commmit_plot(token_data_df, project_commits_list)
    """


    