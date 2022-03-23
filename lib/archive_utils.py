from ast import parse
import typing
from unicodedata import category
from . import database, auth, tweet_utils, config
import requests
import os

# TODO: rewrite this

def archive_media(tweet_id: typing.Union(int, str), user_id: typing.Union(int, str),
    media_tweet_id: typing.Union(int, str), category: str, description: str, flags: list):

    client = auth.get_client()
    api = auth.get_api()

    # Get media tweet
    media_tweet = client.get_tweet(media_tweet_id, user_auth=True, expansions="attachments.media_keys", media_fields="url")
    media_list = []

    for media in media_tweet.includes['media']:
        # Acquire media
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

    # Upload the file and create the tweet 
    media = api.media_upload(file)
    archived = client.create_tweet(text=f"{category} — {description}", media_ids=[media.media_id_string])

    # Update the database
    database.add_media(media_list, category, description, user_id, archived.data['id'])

    # Notify the user
    response = client.create_tweet(text=f"📖 — Esta mídia foi incluída no acervo sob a categoria '{category}'.", in_reply_to_tweet_id=tweet_id, quote_tweet_id=archived.data["id"])
    client.retweet(archived.data["id"])
    return archived



def accept_inclusion_entry(uuid, title_replace=None, overwrite_media_tweet=None):
    print(database.get_request(uuid)[0])
    request_uuid, request_status, tweet_id, user_id, tweet_text, tweet_media, tweet_meta, timestamp = database.get_request(uuid)[0]
    if request_status != "Pendente":
        return False
    text = tweet_text.split("@arquivodojao adicionar ")[-1] if not title_replace else title_replace
    reply = auth.get_api().get_status(tweet_id).in_reply_to_status_id if not overwrite_media_tweet else overwrite_media_tweet

    category, description, text, flags = parse_title()

    tweet = archive_media(reply, user_id, tweet_id, category, description, flags)
    try:
        tweet_utils.send_dms([user_id,], text=f"✅ — Sua solicitação de inclusão de mídia no acervo foi aceita pela moderação.\n\nhttps://twitter.com/arquivodojao/status/{tweet.data['id']}")        
    except:
        pass
    tweet_utils.send_dms(config.get_admin(), text=f"🔮 INFO — Nova inclusão de mídia por meio de solicitação.\n\nhttps://twitter.com/arquivodojao/status/{tweet.data['id']}")
    database.edit_request(request_uuid, "Aceito")
    return True


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
        match word:
            case "-to_gif":
                flags.append("to_gif")
    for flag in flags:
        text = text.replace(" -"+flag, "")
    return category, text, f"{category} — {text}" if category != 'Diverso/Não específico' else text, flags
