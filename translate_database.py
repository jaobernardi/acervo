from lib import auth, database
import threading
import sqlite3
from tqdm import tqdm

def old_query_arbitrary(query):
    con = sqlite3.connect("database old.sql")
    cur = con.cursor()
    cur.execute(query)
    out = [i for i in cur]
    con.commit()
    con.close()
    return out
api = auth.get_client()
client = auth.get_api()

def do_stuff(media_row_old):
    tweet = client.get_status(media_row_old[3].split("/")[-1])

    database.add_tweet(tweet.id, tweet.text, {"in_reply_to_status_id": tweet.in_reply_to_status_id}, None, tweet.user.id)
    database.add_media([media_row_old[1]], media_row_old[-2], media_row_old[2], tweet.user.id, tweet.id)
def translate_media():
    media_rows = [media_row_old for media_row_old in old_query_arbitrary("SELECT * FROM 'media_index' WHERE 1=1")]
    for media_row_old in tqdm(media_rows, "Translating old database stuff", len(media_rows)):
        do_stuff(media_row_old)