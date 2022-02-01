from datetime import datetime
import json
import tweepy

from data import lockbox
import scripts.daily_report as daily_report

DAILY_REPORTS_PATH = "reports/daily"

def setup_api():
    consumer_key = lockbox.TWITTER['consumer_key']
    consumer_secret = lockbox.TWITTER['consumer_secret']
    access_key = lockbox.TWITTER['access_key']
    access_secret = lockbox.TWITTER['access_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return api

def generate_tweet_text(report_date, metric):
    summary_report_dict = daily_report.get_summary_report(report_date)
    token_hashtags = " ".join([f"#{each['token']}" for each in summary_report_dict[metric]])
    if metric == "top_by_num_commits":
        status = "Most active #crypto projects by #github commits today 👨‍💻\n\n"
    if metric == "top_by_num_distinct_authors":
        status = "#crypto project with most developers working on it today 👩‍💻\n\n"
    if metric == "top_by_new_lines":
        status = "Most active #crypto project by new lines of code today 📈\n\n"
    return status + token_hashtags

def post_chart_tweet(api, img_path, tweet_text):
    """this ones actually posts the tweet"""
    print(f"posting img: {img_path}")
    print(tweet_text)
    
    api.update_status_with_media(status=tweet_text, filename=img_path)

def loc_daily_chart(report_date):
    api = setup_api()

    top_loc_img_path = f'reports/daily/{report_date.strftime("%Y-%m-%d")}/top_loc.png'
    loc_tweet_text = generate_tweet_text(report_date, "top_by_new_lines")

    post_chart_tweet(api, top_loc_img_path, loc_tweet_text)

def authors_daily_chart(report_date):
    api = setup_api()

    top_distinct_authors_img_path = f'reports/daily/{report_date.strftime("%Y-%m-%d")}/top_distinct_authors.png'
    authors_tweet_text = generate_tweet_text(report_date, "top_by_num_distinct_authors")

    post_chart_tweet(api, top_distinct_authors_img_path, authors_tweet_text)

def top_commits_daily_chart(report_date):
    api = setup_api()

    top_commits_img_path = f'reports/daily/{report_date.strftime("%Y-%m-%d")}/top_commits.png'
    commits_tweet_text = generate_tweet_text(report_date, "top_by_num_commits")

    post_chart_tweet(api, top_commits_img_path, commits_tweet_text)



if __name__ == "__main__":
    pass