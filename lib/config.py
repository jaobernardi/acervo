import json


def get_stream_url():
    return get_data()['stream_url']

def get_id():
    return get_data()["user_id"]

def get_video_id():
    return get_data()["video_thread"]

def get_admin():
    return get_data()["admin"]

def get_data():
    with open("config.json", "rb") as file:
        data = json.load(file)
    return data

def get_database():
    return get_data()["database"]

def get_bearer():
    return get_data()["bearer_token"]

def get_api_token():
    return get_data()["api_key"]

def get_api_secret():
    return get_data()["api_key_secret"]

def get_access_token():
    return get_data()["access_token"]

def get_image_id():
    return get_data()["image_thread"]

def get_access_token_secret():
    return get_data()["access_token_secret"]
