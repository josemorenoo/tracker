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
    fig.layout.update(yaxis = go.YAxis(title=f"{token} price in USD", side="left"))
    return fig

def create_commits_plot(token: str, token_data_df, project_commits_list):
    # add price plot
    fig = create_price_fig(token, token_data_df)

    # place raw commit fields of interest into a dataframe 
    # this is so that we can create a Hover Text item 
    msg_list = []
    author_list = []
    ms_timestamp_list = []
    in_main_branch_list = []
    files_changed_list = []
    deletions_list = []
    insertions_list = []
    for commit in project_commits_list:
        msg_list.append(commit.msg)
        author_list.append(commit.author.name)
        ms_timestamp_list.append(commit.ms_timestamp)
        in_main_branch_list.append(commit.in_main_branch)
        files_changed_list.append(commit.files)
        deletions_list.append(commit.deletions)
        insertions_list.append(commit.insertions)
    commits_df = pd.DataFrame({
        'msg': msg_list,
        'author': author_list,
        'ms_timestamp': ms_timestamp_list,
        'in_main_branch': in_main_branch_list,
        'files_changed': files_changed_list,
        'deletions': deletions_list,
        'insertions': insertions_list
    })

    # Add each commit to the plot, creating a tooltip that you can hover over which displays info about the commit
    # to do this, we have to use a hovertemplate, which is kind of nasty.

    # If commit msg is short add as-is, otherwise wrap text and add break line tag (<br>)
    def format_commit_msg(msg: str):
        wrapped_msg = textwrap.fill(msg, 30)
        return wrapped_msg.replace('\n', '<br>')
            
    # add each commit as a point on a scatter plot
    # y-axis for now will be lines of code inserted per commit
    fig.add_trace(go.Scatter(
        mode = "markers",
        x = commits_df['ms_timestamp'],
        y = commits_df['insertions'],
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
    fig.layout.update(yaxis2 = go.YAxis(title="Lines Inserted", overlaying='y', side='right', type='log'))
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
    fig.layout.update(yaxis2 = go.YAxis(title="Total # Commits", overlaying='y', side='right'))

    return fig