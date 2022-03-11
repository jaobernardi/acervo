import pyding
import atexit
from lib import database
import tweepy
import logging


@pyding.on("status_ping", priority=100)
def statistics_log(event, status, client, api):
    #database.add_tweet(status.id, status.text, status.media, user_id=status.user.id)
    database.add_mention_entry(status.id, status.text, f"https://twitter.com/{status.user.screen_name}/status/{status.id}")
