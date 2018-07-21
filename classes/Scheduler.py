import sched
import time

from .Bot import Bot

class Scheduler():
    def __init__(self, log):
        self.log = log
        # 1 hour + 30 seconds
        self.update_seconds = (60 * 60) + 30
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def create_bot(self):
        self.bot = Bot(self.log)
        self.bot.work()

    def work(self, sc):
        # create new bot instance and start
        self.create_bot()
        
        # start scheduler again
        self.scheduler.enter(self.update_seconds, 1, self.work, (sc,))

    def start(self):
        # create new bot instance and start
        self.create_bot()
        
        # start scheduler
        self.scheduler.enter(self.update_seconds, 1,
                             self.work, (self.scheduler,))
        self.scheduler.run()