import boto3
from datetime import datetime, timedelta
import random
import time
import traceback
import yaml
import sys
import os

from scripts.paths import RUNTIME_PATHS
import scripts.reporter.periodic_report as periodic_report
import scripts.twitter.post_to_twitter as post
import scripts.twitter.twitter_graphs as graphs

YESTERDAY = datetime.today() - timedelta(hours=24)

def make_report(report_date, mode="DAILY", make_raw_report=True, make_summary_report=True):
    """runs the daily report for today"""
    periodic_report.run(report_date, mode, make_raw_report=make_raw_report, make_summary_report=make_summary_report)

def post_loc_chart(post_to_twitter=True, mode="DAILY", day=YESTERDAY):
    """
    creates and posts graph
    """
    graphs.create_top_by_loc_graph(day, mode=mode)
    if post_to_twitter:
        post.loc_chart(day, mode=mode)

def post_authors_chart(post_to_twitter=True, mode="DAILY", day=YESTERDAY):
    graphs.create_top_by_num_authors_graph(day, mode=mode)
    if post_to_twitter:
        post.authors_chart(day, mode=mode)

def post_commits_chart(post_to_twitter=True, mode="DAILY", day=YESTERDAY):
    graphs.create_top_commits_daily_graph(day, mode=mode)
    if post_to_twitter:
        post.top_commits_chart(day, mode=mode)

def randomize_and_post(funcs, delay_secs, post_to_twitter=True, mode="DAILY", day=YESTERDAY):
    random_order_funcs = random.sample(funcs, len(funcs))
    for f in random_order_funcs:
        f(post_to_twitter, mode=mode, day=day)
        time.sleep(delay_secs)



def make_report_and_post_all_charts(run_report=True,
    post_to_twitter=True,
    mode="DAILY",
    delay_secs=30,
    day=YESTERDAY,
    make_raw_report=True,
    make_summary_report=True):
    """
    Creates daily report and posts all the graphs
    """
    assert mode in ["WEEKLY", "DAILY", "QUARTERLY"]

    if mode=="WEEKLY":
        day = day - timedelta(days=7)

    if mode=="QUARTERLY":
        day = day - timedelta(days=90)

    if run_report:
        make_report(
            report_date=day, 
            mode=mode, 
            make_raw_report=make_raw_report, 
            make_summary_report=make_summary_report
        ) 

    randomize_and_post(funcs=[
        post_loc_chart,
        post_authors_chart,
        post_commits_chart
    ], 
    delay_secs = delay_secs,
    post_to_twitter=post_to_twitter,
    mode=mode,
    day=day)
    
    
def send_text_alert_to_admin(job_failed: bool, error: str):
    try:
        from scripts.keys import KEYS
       
        session = boto3.Session(region_name='us-west-1', aws_secret_access_key=KEYS['secret'], aws_access_key_id=KEYS['key'])
        ses = session.client('ses')

        response = ses.send_email(
            Source='coincommit@gmail.com',
            Destination={
                'ToAddresses': [
                    'coincommit@gmail.com',
                ]
            },
            Message={
                'Subject': {
                    'Data': f"coincommit twitter job {'failed, check ec2' if job_failed else 'succeeded, check twitter'}",
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': 'This is text mail',
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': f'<h1>{error}</h1>',
                        'Charset': 'UTF-8'
                    }
                }
            }
        )


        print("emailing burner account")
    except ImportError:
        print('no AWS keys, no text sent')

if __name__ == "__main__":
    try:
        args = sys.argv
        if len(args) > 1:
            runtime = args[1]
            assert runtime in RUNTIME_PATHS
        else:
            runtime = 'DAILY_RUNTIME'

        # get config values for this runtime (daily, weekly, etc)
        with open(RUNTIME_PATHS[runtime], 'r') as file:
            config = yaml.safe_load(file)
            run_report: bool = config['run_report']
            post_to_twitter: bool = config['post_to_twitter']
            mode: str = config['mode']
            delay_secs: int =config['delay_secs']
            make_raw_report: bool =config['make_raw_report']
            make_summary_report: bool =config['make_summary_report']
            print(*config.items(), sep="\n")

        # run everything
        make_report_and_post_all_charts(
            run_report=run_report,
            post_to_twitter=post_to_twitter,
            mode=mode,
            delay_secs=delay_secs,
            make_raw_report=make_raw_report, 
            make_summary_report=make_summary_report)
    except Exception as ex:
        with open('runtime_error_log.txt', 'w') as f:
            f.write("".join(traceback.TracebackException.from_exception(ex).format()))
        os.system("aws ec2 stop-instances --instance-ids i-093f3ffd4fc008b57")
    
