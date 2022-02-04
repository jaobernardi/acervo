import sqlite3
from datetime import datetime
import uuid

def setup_tables():
    con = sqlite3.connect("database.sql")
    cur = con.cursor()

    cur.execute("CREATE TABLE `status_mention` (`id` INT(32), `text` MEDIUMTEXT, `link` TEXT, `time` DATETIME);")
    cur.execute("CREATE TABLE `add_queue` (`uuid` TEXT(36), `tweet_id` INT(32), `text` MEDIUMTEXT, `link` TEXT, `time` DATETIME, user TEXT);")
    cur.execute("CREATE TABLE `media_index` (`uuid` TEXT(36), `media_id` MEDIUMTEXT, `text` MEDIUMTEXT, `link` TEXT, `time` DATETIME, `category` TEXT, `type` TEXT);")
    con.commit()
    con.close()


def arbitrary_query(query):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def add_mention_entry(id, text, link):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("INSERT INTO `status_mention`(`id`, `text`, `link`, `time`) VALUES (?, ?, ?, ?)", (id, text, link, datetime.now()))
    con.commit()
    con.close()


def add_inclusion_entry(tweet_id, text, link, user):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    id = str(uuid.uuid4())
    cur.execute("INSERT INTO `add_queue`(`uuid`, `tweet_id`, `text`, `link`, `time`, `user`) VALUES (?, ?, ?, ?, ?, ?)", (id, tweet_id, text, link, datetime.now(), user))
    con.commit()
    con.close()
    return id


def clear_video_entries():
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("DELETE FROM `media_index` WHERE 1=1")
    con.commit()
    con.close()


def add_media_entry(media_id, text, category, link, type):
    id = str(uuid.uuid4())
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("INSERT INTO `media_index`(`uuid`, `media_id`, `text`, `link`, `time`, `category`, `type`) VALUES (?, ?, ?, ?, ?, ?, ?)", (id, media_id, text, link, datetime.now(), category, type))
    con.commit()
    con.close()


def get_inclusion_entries(uuid=None):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    output = []
    if not uuid:
        for result in cur.execute("SELECT * FROM `add_queue` WHERE 1=1"):
            output.append(result)
    else:
        for result in cur.execute("SELECT * FROM `add_queue` WHERE `uuid`=?", (uuid,)):
            con.close()
            return result
    con.close()
    return output


def remove_inclusion_entries(uuid):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("DELETE FROM `add_queue` WHERE `uuid`=?", (uuid,))
    con.commit()
    con.close()



def remove_video(uuid):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("DELETE FROM `media_index` WHERE `uuid`=?", (uuid,))
    con.commit()
    con.close()


def get_videos(category=None):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    output = []
    if not category:
        for result in cur.execute("SELECT * FROM `media_index` WHERE `type`='video'"):
            output.append(result)
    else:
        for result in cur.execute("SELECT * FROM `media_index` WHERE `type`='video', `category`=?", (category,)):
            output.append(result)
    con.close()
    return output


def get_photos(category=None):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    output = []
    if not category:
        for result in cur.execute("SELECT * FROM `media_index` WHERE `type`='photo'"):
            output.append(result)
    else:
        for result in cur.execute("SELECT * FROM `media_index` WHERE `type`='photo', `category`=?", (category,)):
            output.append(result)
    con.close()
    return output


def get_media(category=None):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    output = []
    if not category:
        for result in cur.execute("SELECT * FROM `media_index` WHERE 1=1"):
            output.append(result)
    else:
        for result in cur.execute("SELECT * FROM `media_index` WHERE `category`=?", (category,)):
            output.append(result)
    con.close()
    return output



def get_mentions():
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    output = []
    for result in cur.execute("SELECT * FROM `status_mention` WHERE 1=1"):
        output.append(result)
    con.close()
    return output
