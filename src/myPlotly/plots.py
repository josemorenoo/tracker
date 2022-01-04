from os import truncate
from re import template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import textwrap

from Stats import Stats

def create_price_fig(token, token_data_df):
    """Used by most of the plots below, just a utility function to create the token price fig"""
    fig = px.line(token_data_df, x='ms_timestamp', y="close")
    fig.layout.update(yaxis = go.layout.YAxis(title=f"{token} price in USD", side="left"))
    fig.update_layout(yaxis_tickformat = '$')
    return fig

def create_commits_plot(token: str, token_data_df, project_commits_list, commits_df):
    # add price plot
    fig = create_price_fig(token, token_data_df)

    # Add each commit to the plot, creating a tooltip that you can hover over which displays info about the commit
    # to do this, we have to use a hovertemplate, which is kind of nasty.

    # If commit msg is short add as-is, otherwise wrap text and add break line tag (<br>)
    def format_commit_msg(msg: str):
        wrapped_msg = textwrap.fill(msg, 30)
        return wrapped_msg.replace('\n', '<br>')
            
    # add each commit as a point on a scatter plot
    # y-axis for now will be number of files modified per commit
    fig.add_trace(go.Scatter(
        name = "commits",
        mode = "markers",
        x = commits_df['ms_timestamp'],
        y = commits_df['files_changed'],
        hovertemplate = 
        #format_commit_msg(wrapped_commit_lines) + 
        '<br><b>Msg:</b> <%{customdata[0]}<br>'+
        '<br><b>Author:</b> %{customdata[1]}<br>'+
        '<br><b>Files Changed:</b> %{customdata[2]}<br>'+
        '<br><b>+</b>%{customdata[3]} lines<br>'+
        '<br><b>-</b>%{customdata[4]} lines<br>'+
        '<br><b>Merge to Master:</b> %{customdata[5]}<br>'+
        '<br><b>Timestamp:</b> %{customdata[6]}<br>'+
        '<extra></extra>',
        customdata = [[format_commit_msg(c.msg), c.author.name, c.files, c.insertions, c.deletions, c.in_main_branch, c.ms_timestamp] for c in project_commits_list],
        yaxis='y2'
    ))
    fig.layout.update(yaxis2 = go.layout.YAxis(title="# Files Modified Per Commit", overlaying='y', side='right', type='linear'))
    fig.update_layout(hoverlabel_align='left')
    return fig

def create_aggregate_commit_count_plot(token: str, token_data_df, project_commits_list):
    # add price plot
    fig = create_price_fig(token, token_data_df)
    
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
    fig.layout.update(yaxis2 = go.layout.YAxis(title="Total # Commits", overlaying='y', side='right'))

    return fig