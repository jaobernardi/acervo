from concurrent.futures import thread
from re import S
import tweepy
import pyding
from lib import config, stream, handlers, auth
import logging
import getpass


logging.basicConfig(level=logging.INFO)

def main():

    # Setup interfaces

    client = auth.get_client()
    api = auth.get_api()

    # Spin up the handlers and call events

    logging.info("Spinning handlers")
    handlers.load_handlers()
    pyding.call("uptime_ping", client=client)

    # Spin up the stream

    logging.info("Spinning stream")
    s = stream.MentionCheck(client, api, config.get_api_token(), config.get_api_secret(), config.get_access_token(), config.get_access_token_secret(), )

    s.filter(track=['arquivodojao'], threaded=True)
    while True:
        command = getpass.getpass("")
        if command == "reload":
            logging.info("Reloading handlers")
            handlers.reload_handlers()
main()


