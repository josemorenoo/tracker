import tweepy

from config.lockbox import TWITTER_KEYS
import scripts.reporter.report_util as util

from scripts.twitter.graph_names import GRAPH_NAMES

DAILY_REPORTS_PATH = "reports/daily"

def setup_api():
    consumer_key = TWITTER_KEYS['consumer_key']
    consumer_secret = TWITTER_KEYS['consumer_secret']
    access_key = TWITTER_KEYS['access_key']
    access_secret = TWITTER_KEYS['access_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return api

def generate_tweet_text(report_date, metric, mode="DAILY"):
    summary_report_dict = util.get_summary_report(report_date, mode)
    token_hashtags = " ".join([f"#{each['token']}" for each in summary_report_dict[metric]])

    if mode == "DAILY":
        when = 'today'
    if mode == "WEEKLY":
        when = 'this week'

    if metric == "top_by_num_commits":
        status = f"Most active #crypto projects by #github commits {when} 👨‍💻\n\n"
    if metric == "top_by_num_distinct_authors":
        status = f"#crypto project with most developers working on it {when} 👩‍💻\n\n"
    if metric == "top_by_new_lines":
        status = f"Most active #crypto project by new lines of code {when} 📈\n\n"
    return status + token_hashtags

def post_chart_tweet(api, img_path, tweet_text):
    """this ones actually posts the tweet"""
    print(f"posting img: {img_path}")
    print(tweet_text)
    
    api.update_status_with_media(status=tweet_text, filename=img_path)

def loc_chart(report_date, mode="DAILY"):
    api = setup_api()

    top_loc_img_path = f'reports/{mode.lower()}/{report_date.strftime("%Y-%m-%d")}/{GRAPH_NAMES["LOC_AND_PRICE"]}'
    loc_tweet_text = generate_tweet_text(report_date, "top_by_new_lines", mode=mode)

    post_chart_tweet(api, top_loc_img_path, loc_tweet_text)
    

def authors_chart(report_date, mode="DAILY"):
    api = setup_api()

    top_distinct_authors_img_path = f'reports/{mode.lower()}/{report_date.strftime("%Y-%m-%d")}/{GRAPH_NAMES["AUTHORS_AND_PRICE"]}'
    authors_tweet_text = generate_tweet_text(report_date, "top_by_num_distinct_authors", mode=mode)

    post_chart_tweet(api, top_distinct_authors_img_path, authors_tweet_text)

def top_commits_chart(report_date, mode="DAILY"):
    api = setup_api()

    top_commits_img_path = f'reports/{mode.lower()}/{report_date.strftime("%Y-%m-%d")}/{GRAPH_NAMES[""]}'
    commits_tweet_text = generate_tweet_text(report_date, "top_by_num_commits", mode=mode)

    post_chart_tweet(api, top_commits_img_path, commits_tweet_text)

if __name__ == "__main__":
    pass