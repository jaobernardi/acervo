from . import database, auth, tweet_utils, config
import requests
import os


def rectify_video_entry(tweet_id):
    client = auth.get_client()
    tweet = client.get_tweet(tweet_id, expansions="attachments.media_keys,author_id", user_auth=True)
    title = tweet.data.text
    category, *text = title.split(" — ") if " — " in title else ('Diverso/Não específico', title)  
    media = tweet.includes['media'][0].media_key.split("_")[1]

    database.add_media([media], category, text, tweet.includes['users'][0].id, tweet_id)


def add_media(tweet_id, user_id, original_tweet, title):
    client = auth.get_client()
    api = auth.get_api()
    tweet = client.get_tweet(tweet_id, user_auth=True, expansions="attachments.media_keys", media_fields="url")

    # Check if there is any media in the tweet
    if "media" not in tweet.includes:
        return
    media_list = []
    # Retrieve media
    for media in tweet.includes["media"]:
        if media.type == "animated_gif":
            file = tweet_utils.save_video_as_gif_from_tweet(tweet_id)
            media_type = "gif"

        elif media.type == "video":
            # Retrieve the video
            if "to_gif" in flags:
                file = tweet_utils.save_video_as_gif_from_tweet(tweet_id)
                media_type = "gif"  
            else:
                file = tweet_utils.save_video_from_tweet(tweet_id)
                media_type = "video"                    

        elif media.type == "photo":
            # Retrieve the image
            file = "cache/"+os.path.basename(media.url)
            req = requests.get(media.url, stream=True)
            
            with open(file, "wb") as f:
                for chunk in req.iter_content(1024):
                    f.write(chunk)
            media_type = "photo"
        else:
            break
        media_list.append(api.media_upload(file).media_id_string)

    # Process the indexing
    category, text, title, flags = parse_title(title)           

    # Upload the file and create the tweet 
    media = api.media_upload(file)
    archived = client.create_tweet(text=title, media_ids=[media.media_id_string])

    # Update the database
    database.add_media(media_list, category, text, user_id, original_tweet)

    # Notify the user
    client.retweet(archived.data["id"])
    return archived


def accept_inclusion_entry(uuid, title_replace=None, overwrite_media_tweet=None):
    request_uuid, tweet_id, user_id, tweet_text, tweet_meta, tweet_media, timestamp = database.get_request(uuid)[0]

    text = tweet_text.removeprefix("@arquivodojao adicionar ") if not title_replace else title_replace
    reply = auth.get_api().get_status(tweet_id).in_reply_to_status_id if not overwrite_media_tweet else overwrite_media_tweet
    tweet = add_media(reply, user_id, tweet_id, text)
    try:
        tweet_utils.send_dms([user_id,], text=f"✅ — Sua solicitação de inclusão de mídia no acervo foi aceita pela moderação.\n\nhttps://twitter.com/arquivodojao/status/{tweet.data['id']}")        
    except:
        pass
    tweet_utils.send_dms(config.get_admin(), text=f"🔮 INFO — Nova inclusão de mídia por meio de solicitação.\n\nhttps://twitter.com/arquivodojao/status/{tweet.data['id']}")


def parse_title(title):
    if isinstance(title, list):
        title = " ".join(title)
    title = title.replace("—", "-")
    category, *text = title.split(" - ") if " - " in title else ('Diverso/Não específico', title)
    if not category or category in [" "]:
        category = 'Diverso/Não específico'
    text = " ".join(text)
    flags = []
    for word in text.split(" "):
        print(word)
        match word:
            case "-to_gif":
                flags.append("to_gif")
    for flag in flags:
        text = text.replace(" -"+flag, "")
    return category, text, f"{category} — {text}" if category != 'Diverso/Não específico' else text, flags
