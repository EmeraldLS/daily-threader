import os
import api
from dotenv import load_dotenv
from api_types import Error
import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

load_dotenv()

ACCESS_TOKEN = os.getenv("THREAD_APP_ACCESS_TOKEN")
CLIENT_SECRET = os.getenv("THREAD_APP_CLIENT_SECRET")
CLIENT_ID = os.getenv("THREAD_APP_CLIENT_ID")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

if ACCESS_TOKEN is None or CLIENT_ID is None or CLIENT_SECRET is None or REDIS_HOST is None or REDIS_PORT is None:
    raise ValueError("Some environment variables are not found")

rd = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True)

threadsmeta = api.ThreadsMeta(ACCESS_TOKEN, CLIENT_SECRET, CLIENT_ID)

""" 
Since last day and thread id does not exist yet, the thread id can be nothing, and the last day can be whatever I set it to be.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_daily_thread():
    if not rd.hexists("threads", "last_day"):
        rd.hset("threads", "last_day", "0")
    if not rd.hexists("threads", "last_thread_id"):
        rd.hset("threads", "last_thread_id", "")

    last_day = rd.hget("threads", "last_day")
    last_day = int(last_day) if last_day is not None else 0

    daily_msg = f"""
        Day {last_day + 1} of manifesting that Meta W ✨ @zuck slide me into the dev team, I just know I and the team would go crazy together fr 🤝
    """

    resp = threadsmeta.publish_thread(daily_msg)
    if not isinstance(resp, Error):
        rd.hset("threads", mapping={
            "last_day": str(last_day + 1), 
            "last_thread_id": resp.id
        })

        logger.info("Thread published and Redis updated successfully :)")
    else:
        logger.error(f"Failed to publish thread: {resp.error.message}")

    rd.close()

def main():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(publish_daily_thread, trigger=CronTrigger(hour=13, minute=00), id="daily_thread_job", name="Publish daily thread at 1pm")

        scheduler.start()
        logger.info("Scheduler started successfully :(")
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("Scheduler shutdown successfully")
    
    except Exception as err:
        logger.error(f"Error occured in scheuler setup: {str(err)}")

if __name__ == "__main__":
    main()