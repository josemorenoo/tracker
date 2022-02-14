from datetime import datetime, timedelta
import dataframe_image as dfi
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from tkinter import Y
#from wordcloud import WordCloud



from scripts.twitter.colors import COLORS
from scripts.twitter.graph_names import GRAPH_NAMES
import scripts.twitter.price_delta_supplement as price_delta

from scripts.reporter.paths import PATHS as report_paths
import scripts.reporter.report_util as report_util

def create_img(image_path, fig):
    fig.write_image(image_path)
    print(f"image saved: {image_path}")

def create_file_extension_graphs(tokens_represented, report_date, mode="DAILY", limit=6):
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        title = "Most Modified File Extensions by Project Today"
    if mode=="WEEKLY":
        title = "Most Modified File Extensions by Project This Week"

    for token in tokens_represented:
        # get data
        extension_counts_and_loc_by_token = report_util.get_file_extension_breakdown_from_summary_report(report_date, mode=mode)
        for token, metadata in extension_counts_and_loc_by_token.items():

            # save most common file extensions to dataframe
            token_specific_df = pd.DataFrame(
                metadata[:limit],
                columns=['file extension', 'extension count', 'lines of code affected' ])

            # styling
            token_specific_df.style.set_caption(title)
            df_styled = token_specific_df.style.background_gradient()
            
            # save to image
            TOKEN_SPECIFIC_DIR = f'reports/{mode.lower()}/{report_date_str}/token_specific/'
            if not os.path.exists(TOKEN_SPECIFIC_DIR):
                os.mkdir(TOKEN_SPECIFIC_DIR)
            IMG_PATH = TOKEN_SPECIFIC_DIR + f"{token}_file_extensions.png"
            dfi.export(df_styled, IMG_PATH)


def create_top_by_loc_graph(report_date, mode="DAILY"):

    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        REPORT_DIR = f"{report_paths['DAILY_REPORTS_PATH']}/{report_date_str}"
        title = "Today's Top 10 Tokens by New Lines of Code"
    if mode=="WEEKLY":
        title = "This Week's Top 10 Tokens by New Lines of Code"
        REPORT_DIR = f"{report_paths['WEEKLY_REPORTS_PATH']}/{report_date_str}"
    
    # get data
    by_locs = report_util.get_most_active_by_loc(report_date_str, mode=mode)
    report_util.get_combined_price_deltas(by_locs, report_date, mode)
    #report_util.get_combined_price_deltas(by_locs, report_date, mode)

    # flip so that they show up in descending order on HORIZONTAL bar graph
    by_locs = by_locs[::-1]

    by_locs_df = pd.DataFrame(by_locs, columns=["Token", "New Lines of Code"])

    fig = px.bar(
        by_locs_df,
        title=title,
        x="New Lines of Code",
        y=[f"{token} " for token in by_locs_df['Token']], # Give the damn token label some breathing room
        orientation='h',
        template="plotly_dark" # fig dark background
    )
    fig.update_layout(
        margin=dict(l=130),
        plot_bgcolor=COLORS['background_blue'], # plot dark background
        title = dict(x=0.5, font_size=18), # center title
        font = dict(family='courier'),
        xaxis = dict(
            title = dict(font=dict(size=20)),
            tickfont = dict(size=18)
        ),
        yaxis = dict(
            title = dict(
                text = "Token",
                font=dict(size=20),
                standoff=10 # give the axis title some spacing from the tickers, left spacing is fig margin, see above
            ),
            tickfont = dict(size=18)
        )
    )
    fig.update_traces(
        marker_color=COLORS['loc_pink'],
        textposition='inside',
        text = [f"+{loc_count}" for loc_count in by_locs_df["New Lines of Code"]], # bar graph annotations
        textfont = dict(color=COLORS['background_blue'], size=20)
    )

    # save to image
    image_path = f"{REPORT_DIR}/{GRAPH_NAMES['LOC']}"
    create_img(image_path, fig)

    # add price supplement image
    price_delta.add_price_deltas(
        existing_img_name=GRAPH_NAMES['LOC'],
        new_graph_name=GRAPH_NAMES['LOC_AND_PRICE'],
        report_date=report_date, 
        mode=mode)

def create_top_by_num_authors_graph(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        REPORT_DIR = f"{report_paths['DAILY_REPORTS_PATH']}/{report_date_str}"
        title = "Today's Top 10 Tokens by Distinct Developers"
    if mode=="WEEKLY":
        title = "This Week's Top 10 Tokens by Distinct Developers"
        REPORT_DIR = f"{report_paths['WEEKLY_REPORTS_PATH']}/{report_date_str}"

    # get data
    by_authors = report_util.get_most_active_by_author(report_date_str, mode=mode)
    #report_util.get_combined_price_deltas(by_authors, report_date, mode)

    # flip so that they show up in descending order on HORIZONTAL bar graph
    by_authors = by_authors[::-1]

    by_authors_df = pd.DataFrame(by_authors, columns=["Token", "Number of Distinct Developers"])
    fig = px.bar(
        by_authors_df,
        title=title,
        x="Number of Distinct Developers",
        y=[f"{token} " for token in by_authors_df['Token']], # Give the damn token label some breathing room
        orientation='h',
        template="plotly_dark" # fig dark background
    )
    fig.update_layout(
        margin=dict(l=130),
        plot_bgcolor=COLORS['background_blue'], # plot dark background
        title = dict(x=0.5, font_size=18), # center title
        font = dict(family='courier'),
        xaxis = dict(
            title = dict(font=dict(size=20)),
            tickfont = dict(size=18)
        ),
        yaxis = dict(
            title = dict(
                text = "Token",
                font=dict(size=20),
                standoff=10 # give the axis title some spacing from the tickers, left spacing is fig margin, see above
            ),
            tickfont = dict(size=18)
    )
    )
    fig.update_traces(
        marker_color=COLORS['dev_purple'],
        textposition='inside',
        text = by_authors_df["Number of Distinct Developers"],
        textfont = dict(color=COLORS['background_blue'], size=20)
    )

    # save to image
    image_path = f"{REPORT_DIR}/{GRAPH_NAMES['AUTHORS']}"
    create_img(image_path, fig)

    # add price supplement image
    price_delta.add_price_deltas(
        existing_img_name=GRAPH_NAMES['AUTHORS'],
        new_graph_name=GRAPH_NAMES['AUTHORS_AND_PRICE'],
        report_date=report_date, 
        mode=mode)

def create_top_commits_daily_graph(report_date, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")
    if mode=="DAILY":
        REPORT_DIR = f"{report_paths['DAILY_REPORTS_PATH']}/{report_date_str}"
        title = "Today's Top 10 Tokens by Most Commits"
    if mode=="WEEKLY":
        title = "This Week's Top 10 Tokens by Most Commits"
        REPORT_DIR = f"{report_paths['WEEKLY_REPORTS_PATH']}/{report_date_str}"

    # get data
    by_commits = report_util.get_most_active_by_commits(report_date_str, mode=mode)
    #report_util.get_combined_price_deltas(by_commits, report_date, mode)

    # flip so that they show up in descending order on HORIZONTAL bar graph
    by_commits = by_commits[::-1]

    # create top n commits graph
    by_commits_df = pd.DataFrame(by_commits, columns=["Token", "Number of commits"])
    fig = px.bar(
        by_commits_df,
        title=title,
        x="Number of commits",
        y=[f"{token} " for token in by_commits_df['Token']], # Give the damn token label some breathing room
        orientation='h',
        template="plotly_dark" # fig dark background
    )
    fig.update_layout(
        margin=dict(l=150),
        plot_bgcolor=COLORS['background_blue'], # plot dark background
        title = dict(x=0.5, font_size=22), # center title
        font = dict(family='courier'),
        xaxis = dict(
            title = dict(font=dict(size=20)),
            tickfont = dict(size=18)
        ),
        yaxis = dict(
            title = dict(
                text = "Token",
                font=dict(size=20),
                standoff=10 # give the axis title some spacing from the tickers, left spacing is fig margin, see above
            ),
            tickfont = dict(size=18)
    )
    )
    fig.update_traces(
        marker_color=COLORS['text_green'],
        textposition='inside',
        text = by_commits_df["Number of commits"],
        textfont = dict(color=COLORS['background_blue'], size=20)
    )

    # save to image
    image_path = f"{REPORT_DIR}/{GRAPH_NAMES['COMMITS']}"
    create_img(image_path, fig)

    # add price supplement image
    price_delta.add_price_deltas(
        existing_img_name=GRAPH_NAMES['COMMITS'],
        new_graph_name=GRAPH_NAMES['COMMITS_AND_PRICE'],
        report_date=report_date, 
        mode=mode)


if __name__ == "__main__":
    '''
    create_top_commits_daily_graph()
    create_top_by_num_authors_graph()
    create_top_by_loc_graph()
    '''
    create_file_extension_graphs(['IPC', 'ETH'], datetime(2022, 2, 12), "DAILY")
