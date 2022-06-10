import boto3
from datetime import datetime, timedelta
import random
import time
import yaml
import sys

from scripts.paths import RUNTIME_PATHS, KEYS
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
    assert mode in ["WEEKLY", "DAILY"]

    if mode=="WEEKLY":
        day = day - timedelta(days=7)

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
    
    
def show_jobs(sched):
    #print(f"\n\njobs: {len(sched.get_jobs())}\n")
    for job in sched.get_jobs():
        print("\nname: %s, trigger: %s, next run: %s, handler: %s" % (
          job.name, job.trigger, job.next_run_time, job.func))

def send_text_alert_to_admin(job_failed: bool):
    client = boto3.client('sns',
        aws_access_key_id=KEYS['key'],
        aws_secret_access_key=KEYS['secret'],
        region_name='us-west-1'

    client.publish( 
        PhoneNumber="+14152649114",
        Message=f"coincommit twitter job {'failed, check ec2' if job_failed else 'succeeded, check twitter'}"
    )

if __name__ == "__main__":

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

    # run everything
    try:
        make_report_and_post_all_charts(
            run_report=run_report,
            post_to_twitter=post_to_twitter,
            mode=mode,
            delay_secs=delay_secs,
            make_raw_report=make_raw_report, 
            make_summary_report=make_summary_report)
        send_text_alert_to_admin(job_failed=False)
    except:
        send_text_alert_to_admin(job_failed=True)
