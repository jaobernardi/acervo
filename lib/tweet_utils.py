import requests
import re
import json
from urllib.parse import urlparse
from os import path
from requests_toolbelt import user_agent
import tqdm
from . import database, auth, config


def add_video_from_id(id, title):
    api = auth.get_api()
    client = auth.get_client()

    file = save_video_from_tweet(id)

    category, *text = title.split(" — ") if " — " in title else ('Diverso/Não específico', title) 
                        
    media = api.media_upload(file)
    archived = client.create_tweet(text=title, media_ids=[media.media_id_string], in_reply_to_tweet_id=config.get_video_id())

    database.add_video_entry(media.media_id_string, " ".join(text), category, f"https://twitter.com/arquivodojao/status/{archived.data['id']}")

    client.retweet(archived.data["id"])


def rectify_video_entry(tweet_id):
    client = auth.get_client()
    tweet = client.get_tweet(tweet_id, expansions="attachments.media_keys", user_auth=True)
    title = tweet.data.text
    category, *text = title.split(" — ") if " — " in title else ('Diverso/Não específico', title)  
    media = str(tweet.includes['media'][0].media_key.split("_")[1])

    database.add_video_entry(media, " ".join(text).split("http")[0], category, f"https://twitter.com/arquivodojao/status/{tweet.data['id']}")

def send_request(session, url,method,headers):
    request = session.get(url, headers=headers) if method == "GET" else session.post(url, headers=headers)
    if request.status_code == 200:
        return request.text
    raise Exception()

def get_video(tweet_id):
        log = {}

        # Define our sources
        sources = {
            "video_url" : "https://twitter.com/i/videos/tweet/"+tweet_id,
            "activation_ep" :'https://api.twitter.com/1.1/guest/activate.json',
            "api_ep" : "https://api.twitter.com/1.1/statuses/show.json?id="+tweet_id
        }

        # Requests

        # Set headers and start a session
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0','accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','accept-language' : 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5'}
        session = requests.Session()

        token_request = send_request(session, sources["video_url"], "GET",headers)
        bearer_file = re.findall('src="(.*js)',token_request)
        file_content = send_request(session, str(bearer_file[0]), 'GET',headers)
        bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
        bearer_token = bearer_token_pattern.search(file_content)
        headers['authorization'] = bearer_token.group(0)
        log['bearer'] = bearer_token.group(0)
        req2 = send_request(session, sources['activation_ep'], 'post',headers)
        headers['x-guest-token'] = json.loads(req2)['guest_token']
        log['guest_token'] = json.loads(req2)['guest_token']
        # get link
        log['full_headers'] = headers
        api_request = send_request(session, sources["api_ep"], "GET",headers)

        videos = json.loads(api_request)['extended_entities']['media'][0]['video_info']['variants']
        log['vid_list'] = videos 
        bitrate = 0
        for vid in videos:
            if vid['content_type'] == 'video/mp4':
                    if vid['bitrate'] > bitrate:
                        bitrate = vid['bitrate']
                        hq_video_url = vid['url'] 
        return hq_video_url


def save_video_from_tweet(tweet_id, chunksize=1024):
    tweet_id = str(tweet_id)
    url = get_video(tweet_id)
    url_parsed = urlparse(url)
    filename = path.basename(url_parsed.path)
    r = requests.get(url, stream=True)
    iter = r.iter_content(chunksize)
    with open(f"cache/{filename}", "wb") as file:
        try:
            while chunk := next(iter):
                file.write(chunk)
        except StopIteration:
            return "cache/"+filename


