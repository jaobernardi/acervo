import pyding
import atexit
from lib import database
import logging


@pyding.on("status_ping")
def statistics_log(event, status, client, api):    
    database.add_mention_entry(status.id, status.text, f"https://twitter.com/{status.user.screen_name}/status/{status.id}")


@atexit.register
def goodbye():
    print("Statistics handler disabled.")
    statistics_log.unregister()
