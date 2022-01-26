import sqlite3
from datetime import datetime
import uuid

def setup_tables():
    con = sqlite3.connect("database.sql")
    cur = con.cursor()

    cur.execute("CREATE TABLE `status_mention` (`id` INT(32), `text` MEDIUMTEXT, `link` TEXT, `time` DATETIME);")
    cur.execute("CREATE TABLE `video_index` (`uuid` TEXT(36), `media_id` MEDIUMTEXT, `text` MEDIUMTEXT, `link` TEXT, `time` DATETIME, `category` TEXT);")
    con.commit()
    con.close()


def add_mention_entry(id, text, link):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("INSERT INTO `status_mention`(`id`, `text`, `link`, `time`) VALUES (?, ?, ?, ?)", (id, text, link, datetime.now()))
    con.commit()
    con.close()


def clear_video_entries():
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("DELETE FROM `video_index` WHERE 1=1")
    con.commit()
    con.close()


def add_video_entry(media_id, text, category, link):
    id = str(uuid.uuid4())
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("INSERT INTO `video_index`(`uuid`, `media_id`, `text`, `link`, `time`, `category`) VALUES (?, ?, ?, ?, ?, ?)", (id, media_id, text, link, datetime.now(), category))
    con.commit()
    con.close()
    

def remove_video(uuid):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    cur.execute("DELETE FROM `video_index` WHERE `uuid`=?", (uuid,))
    con.commit()
    con.close()


def get_videos(category=None):
    con = sqlite3.connect("database.sql")
    cur = con.cursor()
    output = []
    if not category:
        for result in cur.execute("SELECT * FROM `video_index` WHERE 1=1"):
            output.append(result)
    else:
        for result in cur.execute("SELECT * FROM `video_index` WHERE `category`=?", (category,)):
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
