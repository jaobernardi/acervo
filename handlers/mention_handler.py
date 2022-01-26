import pyding
from requests_toolbelt import user_agent
from lib import tweet_utils, config, database
import tweepy
import logging
import os

@pyding.on("mention")
def mention(event, status, client: tweepy.Client, api: tweepy.API):
    tokens = [i for i in status.text.split(" ")[1:] if not i.startswith("@")]
    if hasattr(status, "extended_tweet"):
        tokens = [i for i in status.extended_tweet['full_text'].split(" ")[1:] if not i.startswith("@")]
    match tokens:
        case ["adicionar", *title]:
            if status.user.id == 1015394259032313861:
                title = " ".join(title)
                if hasattr(status, "in_reply_to_status_id"):
                    tweet = client.get_tweet(status.in_reply_to_status_id, user_auth=True, expansions="attachments.media_keys")
                    if "media" in tweet.includes:
                        for media in tweet.includes["media"]:
                            if media.type == "video":
                                file = tweet_utils.save_video_from_tweet(status.in_reply_to_status_id)
                                category, *text = title.split(" — ") if " — " in title else ('Diverso/Não específico', title)                                
                                media = api.media_upload(file)
                                archived = client.create_tweet(text=title, media_ids=[media.media_id_string], in_reply_to_tweet_id=config.get_video_id())
                                database.add_video_entry(media.media_id_string, " ".join(text), category, f"https://twitter.com/arquivodojao/status/{archived.data['id']}")
                                response = client.create_tweet(text=f"📖 — Esta mídia foi incluída no acervo sob a categoria '{category}'.", in_reply_to_tweet_id=status.id, quote_tweet_id=archived.data["id"])
                                client.like(status.id)
                                client.retweet(archived.data["id"])