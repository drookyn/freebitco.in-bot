from raven import Client
from dotenv import load_dotenv
import sys
import os

from classes.Log import Log
from classes.Scheduler import Scheduler

# load enviroment variables
load_dotenv(dotenv_path='.env', verbose=True)

def main():
    # load sentry
    sentry_url = os.getenv('SENTRY_URL')
    if sentry_url:
        client = Client(sentry_url)
    
    # create logger
    log = Log()

    try:
        # start scheduler
        scheduler = Scheduler(log)
        scheduler.start()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as error:
        # emit error to logger
        log.logger.error(str(error));

        # emit error to sentry
        if sentry_url:
            client.captureException()
        else:
            pass


if __name__ == '__main__':
    main()
