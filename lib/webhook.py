import json
import requests
from lib import config
import logging
import pyding
from pprint import pprint
import base64
import time


def fetch_data(timeout=2):
    try:
        logging.info("Connecting to webhook stream")
        cred = base64.b64encode(config.get_stream_auth().encode("utf-8")).decode("utf-8")
        req = requests.get(config.get_stream_url(), stream=True, headers={"Authorization": "Basic "+cred})
        if req.status_code == 401:
            logging.error("Failed to authenticate on webhook stream.")
            return
        logging.info("Connected to webhook stream")
        # Fetch data from stream
        data = b""

        for line in req.iter_content():
            # Probably should use .iter_lines() but yolo 
            data += line
            if data.endswith(b"\n"):
                # call events and reset data
                pyding.call("webhook_event", data=json.loads(data))
                data = b""
    except KeyboardInterrupt:
        return

    except requests.exceptions.ConnectionError:
        logging.info("Lost connection to webhook stream")

    time.sleep(timeout)
    logging.info("Trying to reach webhook stream")
    fetch_data(timeout*2)

@pyding.on("webhook_event")
def webhook(event, data):
    if "favorite_events" in data:
        for tweet in data['favorite_events']:
            pyding.call("tweet_like", tweet=tweet['favorited_status']['id'], data=tweet)
    
    if "direct_message_events" in data:
        for dm in data['direct_message_events']:
            if dm['type'] == "message_create":
                pyding.call("direct_message",
                    message=dm['message_create']['message_data']['text'],
                    meta=dm['message_create']['message_data']['entities'],
                    sender_id=dm['message_create']['sender_id'],
                    user=data['users'][dm['message_create']['sender_id']],
                    data=dm
                )
    return