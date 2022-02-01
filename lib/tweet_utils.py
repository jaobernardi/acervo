from unicodedata import decimal
import requests
import re
import json
from urllib.parse import urlparse
from os import path, system
from requests_toolbelt import user_agent
import tqdm
from . import database, auth, config
import ffmpy
import uuid
import subprocess
import os


def send_dms(recipients, *args, **kwargs):
    api = auth.get_api()
    out = []
    for id in recipients:
        out.append(api.send_direct_message(id, *args, **kwargs))
    return out


def send_request(session, url,method,headers):
    request = session.get(url, headers=headers) if method == "GET" else session.post(url, headers=headers)
    if request.status_code == 200:
        return request.text
    raise Exception()


def get_video(tweet_id):
    #—————————————————————————————————————————————————————————————————————————————————————————
    # Retrieved partially from https://github.com/f-rog/twitter2mp4/blob/master/twitter2mp4.py 
    # ❤️ — Big thanks
    #—————————————————————————————————————————————————————————————————————————————————————————

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
                if vid['bitrate'] >= bitrate:
                    bitrate = vid['bitrate']
                    hq_video_url = vid['url'] 
    return hq_video_url


def save_video_as_gif_from_tweet(tweet_id, chunksize=1024):
    filename = save_video_from_tweet(tweet_id)

    system(f'ffmpeg -i {filename} {filename.removesuffix(".mp4")}.gif -loglevel quiet')

    return filename.removesuffix(".mp4")+".gif"


def save_video_from_tweet(tweet_id, chunksize=1024):
    tweet_id = str(tweet_id)
    url = get_video(tweet_id)
    r = requests.get(url, stream=True)
    filename = uuid.uuid4()
    with open(f"cache/{filename}.mp4", "wb") as file:
        for chunk in r.iter_content(chunksize):
            file.write(chunk)
    return f"cache/{filename}.mp4"

