from . import database, auth


def rectify_video_entry(tweet_id):
    client = auth.get_client()
    tweet = client.get_tweet(tweet_id, expansions="attachments.media_keys", user_auth=True)
    title = tweet.data.text
    category, *text = title.split(" — ") if " — " in title else ('Diverso/Não específico', title)  
    media = str(tweet.includes['media'][0].media_key.split("_")[1])

    database.add_media_entry(media, " ".join(text).split("http")[0], category, f"https://twitter.com/arquivodojao/status/{tweet.data['id']}", "video")
