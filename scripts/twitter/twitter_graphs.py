from datetime import datetime, timedelta
from tkinter import Y
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
#from wordcloud import WordCloud

from scripts.twitter.colors import COLORS
from scripts import daily_report

DAILY_REPORTS_PATH = 'reports/daily/'

def create_img(image_path, fig):
    fig.write_image(image_path)
    print(f"image saved: {image_path}")

def create_top_by_loc_graph(report_date):
    report_date_str = report_date.strftime("%Y-%m-%d")
    REPORT_DIR = f"{DAILY_REPORTS_PATH}{report_date_str}"
    # get data
    _, by_locs, _ = daily_report.get_top_most_active(report_date_str)

    # flip so that they show up in descending order on HORIZONTAL bar graph
    by_locs = by_locs[::-1]

    by_locs_df = pd.DataFrame(by_locs, columns=["Token", "New Lines of Code"])
    fig = px.bar(
        by_locs_df,
        title=f"Today's Top 10 Tokens by New Lines of Code",
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
    image_path = f"{REPORT_DIR}/top_loc.png"
    create_img(image_path, fig)

def create_top_by_num_authors_graph(report_date):
    report_date_str = report_date.strftime("%Y-%m-%d")
    REPORT_DIR = f"{DAILY_REPORTS_PATH}{report_date_str}"
    # get data
    _, _, by_authors = daily_report.get_top_most_active(report_date_str)

    # flip so that they show up in descending order on HORIZONTAL bar graph
    by_authors = by_authors[::-1]

    by_authors_df = pd.DataFrame(by_authors, columns=["Token", "Number of Distinct Developers"])
    fig = px.bar(
        by_authors_df,
        title=f"Today's Top 10 Tokens by Distinct Developers",
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
    image_path = f"{REPORT_DIR}/top_distinct_authors.png"
    create_img(image_path, fig)

def create_top_commits_daily_graph(report_date):
    report_date_str = report_date.strftime("%Y-%m-%d")
    REPORT_DIR = f"{DAILY_REPORTS_PATH}{report_date_str}"

    # get data
    by_commits, _, _ = daily_report.get_top_most_active(report_date_str)

    # flip so that they show up in descending order on HORIZONTAL bar graph
    by_commits = by_commits[::-1]

    # create top n commits graph
    by_commits_df = pd.DataFrame(by_commits, columns=["Token", "Number of commits"])
    fig = px.bar(
        by_commits_df,
        title=f"Today's Top 10 Tokens by Commit Count",
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
    image_path = f"{REPORT_DIR}/top_commits.png"
    create_img(image_path, fig)

def create_word_cloud_daily_graph(report_date):
    """not very useful visually, we would need to filter for unusual words"""
    daily_report_word_set = daily_report.get_commit_message_word_list(report_date)

    from collections import Counter

    print(*Counter(daily_report_word_set).most_common(40), sep="\n")

    word_cloud_exclusions = [
        "Close", "Co", "Authored", "update", "fix", "build", "by", "github",
        "Closes", "output", "com", "tar", "gz", "json", "[", "]", "fix", "fix:",
        "to", "for", "add", "from", "for", "-", "Merge", "the", "request", "pull", "chore",
        "Update", "branch", "in", "a", "of", "is", "and", "test", "token", "automerge", "refactor", "sign", "off"    ]

    # Creating word_cloud with text as argument in .generate() method
    #word_cloud = WordCloud(stopwords=word_cloud_exclusions).generate(" ".join(daily_report_word_set))
    #word_cloud.to_file(f"{REPORT_DIR}/word_cloud.png")
    #test = datetime.today() - timedelta(days=1)
    #word_cloud.to_file(f'{DAILY_REPORTS_PATH}{test.strftime("%Y-%m-%d")}/word_cloud.png')

if __name__ == "__main__":
    #create_word_cloud_daily_graph()
    '''
    # get associated price deltas for each of the top 10 lists from the summary report
    by_commits_price_deltas = daily_report.get_daily_price_deltas([x[0] for x in by_commits], report_date)
    by_loc_price_deltas = daily_report.get_daily_price_deltas([x[0] for x in by_loc], report_date)
    by_authors_price_deltas = daily_report.get_daily_price_deltas([x[0] for x in by_authors], report_date)

    create_top_commits_daily_graph()
    create_top_by_num_authors_graph()
    create_top_by_loc_graph()
    '''
    
