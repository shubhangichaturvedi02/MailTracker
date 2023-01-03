from apscheduler.schedulers.blocking import BlockingScheduler
from send import send_daily_mail

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=8)
def scheduled_job():
    print('This job is run every weekday at 8 AM.')
    send_daily_mail()
sched.start()