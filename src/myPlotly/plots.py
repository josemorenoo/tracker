import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from Stats import Stats


def create_aggregate_commit_count_plot(token: str, token_data_df, project_commits_list):
    # add price plot
    fig = px.line(token_data_df, x='ms_timestamp', y="close", title=f"Commit Count vs {token} Price")
    
    # set the primary y-axis
    fig.layout.update(yaxis = go.YAxis(title=f"{token} price in USD", side="left"))
    
    # add aggregate commits (need to create a dataframe real quick)
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

    # put the secondary y-axis on the right
    fig.layout.update(yaxis2 = go.YAxis(title="Total # Commits", overlaying='y', side='right'))

    return fig