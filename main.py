from concurrent.futures import thread
from re import S
import pyding
from lib import config, stream, handlers, auth, webhook
import logging


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

    webhook.fetch_data()

main()


