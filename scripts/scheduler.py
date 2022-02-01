from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import random
import time

import scripts.daily_report as daily_report
import scripts.twitter.post_to_twitter as post
import scripts.twitter.twitter_graphs as graphs

YESTERDAY = datetime.today() - timedelta(hours=24)

def run_daily_report(report_date):
    """runs the daily report for today"""
    daily_report.run(report_date)

def post_loc_daily_chart(post_to_twitter=True):
    """
    creates and posts graph
    """
    graphs.create_top_by_loc_graph(YESTERDAY)
    if post_to_twitter:
        post.loc_daily_chart(YESTERDAY)

def post_authors_daily_chart(post_to_twitter=True):
    graphs.create_top_by_num_authors_graph(YESTERDAY)
    if post_to_twitter:
        post.authors_daily_chart(YESTERDAY)

def post_commits_daily_chart(post_to_twitter=True):
    graphs.create_top_commits_daily_graph(YESTERDAY)
    if post_to_twitter:
        post.top_commits_daily_chart(YESTERDAY)

def randomize_and_post(funcs, delays_secs):
    random_order_funcs = random.sample(funcs, len(funcs))
    for f in random_order_funcs:
        f()
        time.sleep(delays_secs)


def make_report_and_post_all_charts():
    """
    Creates daily report and posts all the graphs
    """

    run_daily_report(YESTERDAY) 

    randomize_and_post(funcs=[
        post_loc_daily_chart,
        post_authors_daily_chart,
        post_commits_daily_chart
    ], delays_secs = 300)

    
    
def show_jobs(sched):
    print(f"\n\njobs: {len(sched.get_jobs())}\n")
    for job in sched.get_jobs():
        print("\nname: %s, trigger: %s, next run: %s, handler: %s" % (
          job.name, job.trigger, job.next_run_time, job.func))



if __name__ == "__main__":
    make_report_and_post_all_charts()
    """
    # Start the scheduler
    sched = BackgroundScheduler()
    sched.start()

    hour='10'
    minute='50'
    sched.add_job(make_report_and_post_all_charts, trigger='cron', hour=hour, minute=minute,  day_of_week='*')
    
    # gets job we just created, make sure it starts today if possible
    for job in sched.get_jobs():
        today = datetime.today()
        next_run_time = datetime(
            year = today.year,
            month = today.month,
            day=today.day,
            hour=int(hour),
            minute=int(minute))
        job.modify(next_run_time=next_run_time)

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            show_jobs(sched)
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        sched.shutdown()
    """
    
