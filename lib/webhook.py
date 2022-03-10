import json
import requests
from lib import config
import logging
import pyding
from pprint import pprint


def fetch_data():
    logging.info("Connecting to webhook stream")
    req = requests.get(config.get_stream_url(), stream=True)
    data = b""
    logging.info("Connected to webhook stream")
    for line in req.iter_content():
        data += line
        if data.endswith(b"\n"):
            pyding.call("webhook_event", data=json.loads(data))
            data = b""



@pyding.on("webhook_event")
def webhook(event, data):
    return