import tweepy
import pyding
import logging

class MentionCheck(tweepy.Stream):
    def __init__(self, client, api, *args, **kwargs):
        self.client = client
        self.api = api
        super().__init__(*args, **kwargs)

    def on_status(self, status):
        try:
            logging.info(f"[{status.user.screen_name}] {status.text}")
            event = pyding.call("status_ping", cancellable=True, status=status, client=self.client, api=self.api)
            for entity in status.entities["user_mentions"]:
                if entity['id'] == 1306855576081772544:
                    event = pyding.call("mention", cancellable=True, status=status, client=self.client, api=self.api)
                    break
        except Exception as e:
            print(e)
            pass

    def on_connect(self):
        logging.info("Stream connected")