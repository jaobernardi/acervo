import pyding
import atexit
from lib import database
import tweepy
import logging


@pyding.on("status_ping", priority=100)
def statistics_log(event, status, client, api):
    database.add_tweet(status.id, status.text, {}, [], user_id=status.user.id)

