from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import random
import time

import scripts.reporter.periodic_report as periodic_report
import scripts.twitter.post_to_twitter as post
import scripts.twitter.twitter_graphs as graphs

YESTERDAY = datetime.today() - timedelta(hours=24)

def run_daily_report(report_date, mode="DAILY"):
    """runs the daily report for today"""
    periodic_report.run(report_date, mode)

def post_loc_chart(post_to_twitter=True, mode="DAILY"):
    """
    creates and posts graph
    """
    graphs.create_top_by_loc_graph(YESTERDAY, mode=mode)
    if post_to_twitter:
        post.loc_chart(YESTERDAY, mode=mode)

def post_authors_chart(post_to_twitter=True, mode="DAILY"):
    graphs.create_top_by_num_authors_graph(YESTERDAY, mode=mode)
    if post_to_twitter:
        post.authors_chart(YESTERDAY, mode=mode)

def post_commits_chart(post_to_twitter=True, mode="DAILY"):
    graphs.create_top_commits_daily_graph(YESTERDAY, mode=mode)
    if post_to_twitter:
        post.top_commits_chart(YESTERDAY, mode=mode)

def randomize_and_post(funcs, delay_secs, post_to_twitter=True, mode="DAILY"):
    random_order_funcs = random.sample(funcs, len(funcs))
    for f in random_order_funcs:
        f(post_to_twitter, mode=mode)
        time.sleep(delay_secs)



def make_report_and_post_all_charts(run_report=True, post_to_twitter=True, mode="DAILY", delay_secs=30):
    """
    Creates daily report and posts all the graphs
    """

    if run_report:
        run_daily_report(YESTERDAY, mode=mode) 

    randomize_and_post(funcs=[
        post_loc_chart,
        post_authors_chart,
        post_commits_chart
    ], 
    delay_secs = delay_secs,
    post_to_twitter=post_to_twitter,
    mode=mode)
    
    
def show_jobs(sched):
    print(f"\n\njobs: {len(sched.get_jobs())}\n")
    for job in sched.get_jobs():
        print("\nname: %s, trigger: %s, next run: %s, handler: %s" % (
          job.name, job.trigger, job.next_run_time, job.func))



if __name__ == "__main__":
    make_report_and_post_all_charts(run_report=False, post_to_twitter=False, mode='DAILY', delay_secs=0)
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
    
