import pyding
from lib import tweet_utils, config, database
import tweepy
import os
import requests
from urllib.parse import quote

from lib.archive_utils import parse_title
from lib.media_utils import lower_image_quality

@pyding.on("mention")
def mention(event, status, client: tweepy.Client, api: tweepy.API):
    # Get the message tokens
    tokens = [i for i in status.text.split(" ")[1:] if not i.startswith("@")]
    if hasattr(status, "extended_tweet"):
        tokens = [i for i in status.extended_tweet['full_text'].split(" ")[1:] if not i.startswith("@")]

    match tokens:
        case ["beta_features", "baixar" | "download"]:
            client.create_tweet(text=f"📸 — Esta mídia está disponível para download em: https://services.jaobernardi.space/twitter/video/{status.in_reply_to_status_id}", in_reply_to_tweet_id=status.id)

        case ["beta_features", "low_poly", *args]:
            if status.in_reply_to_status_id:                
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
            media_list = []
            # Retrieve media
            for media in tweet.includes["media"]:
                if media.type == "photo":
                    # Retrieve the image
                    file = "cache/"+os.path.basename(media.url)
                    req = requests.get(media.url, stream=True)
                    
                    with open(file, "wb") as f:
                        for chunk in req.iter_content(1024):
                            f.write(chunk)
                    low_poly = lower_image_quality(file, 40, 15)
                    media_list.append(api.media_upload(low_poly).media_id_string)
            if media_list:
                client.create_tweet(text=f"🔮 — Imagem destruída com sucesso", media_ids=media_list, in_reply_to_tweet_id=status.id)
                           
        case ["adicionar", *title]:
            # Check if author is an admin (placeholder solution)
            if status.user.id not in config.get_admin():
                client.create_tweet(text=f"🔮 — Sua solicitação de inclusão será submetida a análise e poderá ser aceita ou indeferida. ;)\n\n(Você pode acompanhar a situação da sua solicitação pela DM)", direct_message_deep_link="https://twitter.com/messages/compose?recipient_id=1306855576081772544&text=Qual%20a%20situa%C3%A7%C3%A3o%20dos%20meus%20pedidos?", in_reply_to_tweet_id=status.id)
                id = database.add_request(status.user.id, status.id)

                options = [
                    {
                        "label": "Aprovar e Editar título",
                        "description": "Solicitação ficará aprovada com um novo título.",
                        "metadata": f"requests:approved:edit:{id}"
                    },
                    {
                        "label": "Aprovado",
                        "description": "Solicitação ficará aprovada.",
                        "metadata": f"requests:approved:{id}"
                    },
                    {
                        "label": "Indeferido",
                        "description": "Solicitação ficará indeferida por ser duplicata ou inadequada.",
                        "metadata": f"requests:reject:{id}"
                    }
                ]
                tweet_utils.send_dms(config.get_admin(), text=f"Olá! O seguinte requerimento aguarda deferimento:\nhttps://twitter.com/{status.user.screen_name}/status/{status.id}", quick_reply_options=options)
                return
            
            # Check if it is an reply
            if status.in_reply_to_status_id:                
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
            media_list = []
            # Process the indexing
            category, text, title, flags = parse_title(title)  
            # Retrieve media
            for media in tweet.includes["media"]:
                if media.type == "animated_gif":
                    file = tweet_utils.save_video_as_gif_from_tweet(status.in_reply_to_status_id)
                    media_type = "gif"

                elif media.type == "video":
                    # Retrieve the video
                    if "to_gif" in flags:
                        file = tweet_utils.save_video_as_gif_from_tweet(status.in_reply_to_status_id)
                        media_type = "gif"  
                    else:
                        file, url = tweet_utils.save_video_from_tweet(status.in_reply_to_status_id, return_url=True)
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
            
            archived = client.create_tweet(text=title, media_ids=media_list)
            # Add download if needed
            if media_type == "video":
                response = client.create_tweet(text=f"📸 — Esta mídia está disponível para download em: https://services.jaobernardi.space/twitter/video/url/{quote(url, safe='')}", in_reply_to_tweet_id=archived.data['id'])

            # Update the database
            database.add_media(media_list, category, text, status.user.id, status.id)

            # Notify the user
            response = client.create_tweet(text=f"📖 — Esta mídia foi incluída no acervo sob a categoria '{category}'.", in_reply_to_tweet_id=status.id, quote_tweet_id=archived.data["id"])
            client.retweet(archived.data["id"])
            return
    