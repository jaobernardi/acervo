from . import config
import logging
import tweepy


def get_auth():
    auth = {
        "consumer_key": config.get_api_token(),
        "consumer_secret": config.get_api_secret(),
        "access_token": config.get_access_token(),
        "access_token_secret": config.get_access_token_secret(),
    }
    return auth

def get_client():
    auth = get_auth()
    logging.info("Connecting client interface ")
    return tweepy.Client(**auth)


def get_api():
    auth = get_auth()
    auth = tweepy.OAuth1UserHandler(**auth)
    logging.info("Connecting Api 1.1 interface")
    return tweepy.API(auth)