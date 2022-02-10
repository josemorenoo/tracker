from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import textwrap

from ..stats_util import Stats

# xaxis formatting
# https://stackoverflow.com/questions/52339903/plotly-how-to-plot-just-month-and-day-on-x-axis-ignore-year

class Plots:

    # monthname DD linebreak YYYY
    XAXIS_TICKFORMAT = '%B %d<br>%Y'

    def float_epoch_ts_to_datetime(ms_timestamps):
        return [datetime.fromtimestamp(int(str(ms)[:10])) for ms in ms_timestamps]

    def create_commits_plot(token: str, token_data_df, project_commits_list, commits_df):
        fig = Plots.create_price_fig(token, token_data_df)

        # Add each commit to the plot, creating a tooltip that you can hover over which displays info about the commit
        # to do this, we have to use a hovertemplate, which is kind of nasty.
                
        # add each commit as a point on a scatter plot
        # y-axis for now will be number of files modified per commit
        customdata = Plots.create_commit_custom_data_for_hover_template(project_commits_list)
        fig.add_trace(go.Scatter(
            name = "Commits",
            mode = "markers",
            x = Plots.float_epoch_ts_to_datetime(commits_df['ms_timestamp']),
            y = commits_df['files_changed'],
            hovertemplate = Plots.create_commit_hover_template(),
            customdata = customdata,
            yaxis='y2'
        ))
        fig.layout.update(
            yaxis2 = go.layout.YAxis(title="# Files Modified Per Commit",
            overlaying='y',
            side='right',
            type='linear'))
        fig.update_layout(
            hoverlabel_align='left')
        return fig

    def create_aggregate_commit_count_plot(token: str, token_data_df, project_commits_list):
        fig = Plots.create_price_fig(token, token_data_df)
        
        # add aggregate commits (need to create a dataframe real quick)
        ts_bucket_list, commits_per_bucket = Stats.calculate_commit_count_in_range(project_commits_list, "5min")
        commits_df = pd.DataFrame({
            'ms_timestamp': ts_bucket_list,
            'commits_per_5min_range': commits_per_bucket 
        })

        # add number of commits for each 5min window
        fig.add_trace(go.Scatter(
            name="Aggregate # of Commits",
            mode="markers",
            x=Plots.float_epoch_ts_to_datetime(commits_df["ms_timestamp"]),
            y=commits_df["commits_per_5min_range"],
            marker = {'color': "cyan"},
            hovertemplate = '<br><b>Project Commit Count:</b> %{y}<br>'+'<extra></extra>',
            yaxis='y2'))

        # put the secondary y-axis on the right
        fig.layout.update(
            yaxis2 = go.layout.YAxis(title="Total # Commits",
            overlaying='y',
            side='right'))
        return fig

    def create_lines_of_code_plot(token: str, token_data_df, project_commits_list):
        fig = Plots.create_price_fig(token, token_data_df)

        lines_of_code, commit_ms_timestamp = Stats.calculate_lines_of_code_count(project_commits_list)
        fig.add_trace(go.Scatter(
            name = "Lines of Code",
            mode = "lines+markers",
            x = Plots.float_epoch_ts_to_datetime(commit_ms_timestamp),
            y = lines_of_code,
            marker = {'color': "blueviolet"},
            line = {'color': "blueviolet"},
            hovertemplate = '<br><b>Lines of Code: </b> %{y}<br>'+'<extra></extra>',
            yaxis='y2'
        ))
        fig.layout.update(
            yaxis2 = go.layout.YAxis(title=f"Lines of Code",
            overlaying='y',
            side='right',
            type='linear'))
        fig.update_layout(
            hoverlabel_align='left')
        return fig

    def create_number_of_authors_plot(token: str, token_data_df, project_commits_list):
        fig = Plots.create_price_fig(token, token_data_df)

        authors_count, author_names_list, new_author_timestamps = Stats.calculate_running_number_of_authors(project_commits_list)
        fig.add_trace(go.Scatter(
            name = "Number of Authors",
            mode = "lines+markers",
            x = Plots.float_epoch_ts_to_datetime(new_author_timestamps),
            y = authors_count,
            line = {'color': "aqua"},
            marker = {'color': "aqua"},
            hovertemplate = '<br><b>Number of Authors:</b> %{y}<br>'+\
            '<br><b>New Author:</b> %{customdata}<br>'+\
            '<extra></extra>',
            customdata=author_names_list,
            yaxis='y2'
        ))

        fig.layout.update(yaxis2 = go.layout.YAxis(title=f"Number of Authors", overlaying='y', side='right', type='linear'))
        fig.update_layout(
            hoverlabel_align='left'
        )
        return fig

    def create_price_fig(token, token_data_df):
        """Used by most of the plots below, just a utility function to create the token price fig"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            name=f"{token} Price",
            mode="lines",
            x=Plots.float_epoch_ts_to_datetime(token_data_df["ms_timestamp"]),
            y=token_data_df["close"],
            hovertemplate='<br><b>Price: </b> %{y}<br>'+'<extra></extra>'
        ))
        fig.layout.update(yaxis = go.layout.YAxis(title=f"{token} price in USD", side="left"))
        fig.update_layout(yaxis_tickformat = '$', xaxis_tickformat=Plots.XAXIS_TICKFORMAT)
        return fig

    def create_commit_hover_template():
        """creates a template for what shows up when you hover over a commit. Needs custom data, see function below"""
        return '<br><b>Msg:</b> <%{customdata[0]}<br>'+\
            '<br><b>Author:</b> %{customdata[1]}<br>'+\
            '<br><b>Files Changed:</b> %{customdata[2]}<br>'+\
            '<br><b>+</b>%{customdata[3]} lines<br>'+\
            '<br><b>-</b>%{customdata[4]} lines<br>'+\
            '<br><b>Merge to Master:</b> %{customdata[5]}<br>'+\
            '<br><b>Timestamp:</b> %{customdata[6]}<br>'+\
            '<extra></extra>'

    def create_commit_custom_data_for_hover_template(project_commits_list):
        # If commit msg is short add as-is, otherwise wrap text and add break line tag (<br>)
        def format_commit_msg(msg: str):
            max_msg_width = 30
            wrapped_msg = textwrap.fill(msg, max_msg_width)
            return wrapped_msg.replace('\n', '<br>') # html uses line breaks <br> instead of newline

        return [[
            format_commit_msg(c.msg),
            c.author.name,
            c.files,
            c.insertions,
            c.deletions,
            c.in_main_branch,
            c.ms_timestamp] for c in project_commits_list]