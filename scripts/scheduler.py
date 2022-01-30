from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time

import scripts.daily_report as daily_report
import scripts.twitter.post_to_twitter as post
import scripts.twitter.twitter_graphs as graphs

def run_daily_report():
    """runs the daily report for today"""
    daily_report.run()

def post_loc_daily_chart():
    """
    creates and posts graph
    """
    graphs.create_top_by_loc_graph()
    post.loc_daily_chart(datetime.today())

def post_authors_daily_chart():
    graphs.create_top_by_num_authors_graph()
    post.authors_daily_chart(datetime.today())

def post_commits_daily_chart():
    graphs.create_top_commits_daily_graph()
    post.top_commits_daily_chart(datetime.today())

def make_report_and_post_all_charts():
    """
    Creates daily report and posts all the graphs
    """

    run_daily_report()
    post_loc_daily_chart()
    time.sleep(200)
    post_authors_daily_chart()
    time.sleep(200)
    post_commits_daily_chart()
    
def show_jobs():
    print(f"\n\njobs: {len(sched.get_jobs())}\n")
    for job in sched.get_jobs():
        print("\nname: %s, trigger: %s, next run: %s, handler: %s" % (
          job.name, job.trigger, job.next_run_time, job.func))



if __name__ == "__main__":
    # Start the scheduler
    sched = BackgroundScheduler()
    sched.start()

    hour='22'
    minute='01'
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
            show_jobs()
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        sched.shutdown()
