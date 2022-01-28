from nis import cat
from attr import has
import pyding
from requests_toolbelt import user_agent
from lib import tweet_utils, config, database
import tweepy
import logging
import os
import requests

@pyding.on("mention")
def mention(event, status, client: tweepy.Client, api: tweepy.API):
    # Get the message tokens
    tokens = [i for i in status.text.split(" ")[1:] if not i.startswith("@")]
    if hasattr(status, "extended_tweet"):
        tokens = [i for i in status.extended_tweet['full_text'].split(" ")[1:] if not i.startswith("@")]

    match tokens:
        case ["adicionar", *title]:
            # Check if author is an admin (placeholder solution)
            if status.user.screen_name not in config.get_admin():
                return
            
            # Check if it is an reply
            if hasattr(status, "in_reply_to_status_id"):                
                # Retrieve original tweet
                tweet_id = status.in_reply_to_status_id
            else:
                # Get the status
                tweet_id = status.id

            tweet = client.get_tweet(tweet_id, user_auth=True, expansions="attachments.media_keys", media_fields="url")

            # Check if there is any media in the tweet
            if "media" not in tweet.includes:
                return
            
            # Signal acknowledgement
            client.like(status.id)

            # Retrieve media
            for media in tweet.includes["media"]:
                if media.type == "animated_gif":
                    file = tweet_utils.save_video_as_gif_from_tweet(status.in_reply_to_status_id)
                    media_type = "gif"
                    break

                elif media.type == "video":
                    # Retrieve the video
                    file = tweet_utils.save_video_from_tweet(status.in_reply_to_status_id)
                    media_type = "video"
                    break

                elif media.type == "photo":
                    # Retrieve the image
                    file = "cache/"+os.path.basename(media.url)
                    req = requests.get(media.url, stream=True)
                    
                    with open(file, "wb") as f:
                        for chunk in req.iter_content(1024):
                            f.write(chunk)
                    media_type = "photo"
                    break
                        
            # Process the indexing
            title = " ".join(title)
            title = title.replace("—", "-")
            category, *text = title.split(" - ") if " - " in title else ('Diverso/Não específico', title)
            if not category or category in [" "]:
                category = 'Diverso/Não específico'
            title = f"{category} — {' '.join(text)}" if category != 'Diverso/Não específico' else " ".join(text)

            # Upload the file and create the tweet 
            media = api.media_upload(file)
            archived = client.create_tweet(text=title, media_ids=[media.media_id_string], in_reply_to_tweet_id=config.get_image_id())

            # Update the database
            database.add_media_entry(media.media_id_string, " ".join(text), category, f"https://twitter.com/arquivodojao/status/{archived.data['id']}", media_type)

            # Notify the user
            response = client.create_tweet(text=f"📖 — Esta mídia foi incluída no acervo sob a categoria '{category}'.", in_reply_to_tweet_id=status.id, quote_tweet_id=archived.data["id"])
            client.retweet(archived.data["id"])
            return