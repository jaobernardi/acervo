import sqlite3
from datetime import datetime

import json
from . import config
import uuid

def setup_tables():
    con = sqlite3.connect(config.get_database())
    cur = con.cursor()

    users = """
    CREATE TABLE Users (
        `UserID` INT(36),
        `UserUUID` TEXT(36)
    )
    """

    tweets = """
    CREATE TABLE Tweets (
        `TweetID` INT(36),
        `TweetUUID` TEXT(36),
        `UserUUID` TEXT(36),
        `TweetText` TEXT(290),
        `TweetMeta` MEDIUMTEXT,
        `TweetMedia` TEXT(128),
        `Timestamp` DATETIME,
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID)
    )
    """

    media = """
    CREATE TABLE Media (
        `MediaUUID` TEXT(36),
        `MediaID` INT(36),        
        `UserUUID` TEXT(36),
        `TweetUUID` TEXT(36),
        `MediaCategory` TEXT,
        `MediaDescription` TEXT,
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID),
        FOREIGN KEY(TweetUUID) REFERENCES Tweets(TweetUUID)
    )
    """

    inclusion_queue = """
    CREATE TABLE RequestQueue (
        `RequestUUID` TEXT(36),
        `TweetUUID` TEXT(36),
        `UserUUID` TEXT(36),
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID),
        FOREIGN KEY(TweetUUID) REFERENCES Tweets(TweetUUID)
    )
    """

    cur.execute(users)
    cur.execute(tweets)
    cur.execute(media)
    cur.execute(inclusion_queue)

    con.commit()
    con.close()

class DatabaseConnection(object):
    def __enter__(self):
        self.connection = sqlite3.connect(config.get_database())
        return self.connection.cursor()
    
    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


# User manipulation methods
def add_user(user_id):
    user_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, str(user_id)))
    with DatabaseConnection() as cursor:
        if not get_user(user_uuid):
            cursor.execute("INSERT INTO Users(UserID, UserUUID) VALUES (?, ?)", (user_id, user_uuid))
    return user_uuid


def get_user(user_uuid=None):
    with DatabaseConnection() as cursor:
        if not user_uuid:
             user = [i for i in cursor.execute("SELECT * FROM Users WHERE 1=1")]
        else:
            user = [i for i in cursor.execute("SELECT * FROM Users WHERE UserUUID=?", (user_uuid,))]
    return user[0] if len(user) == 1 else user


def delete_user(user_uuid):
    with DatabaseConnection() as cursor:
        cursor.execute("DELETE FROM Users WHERE UserUUID=?", (user_uuid,))


# Tweet manipulation methods
def add_tweet(tweet_id, tweet_text, tweet_meta, tweet_media, user_uuid=None, user_id=None):
    if not user_id and not user_uuid:
        return    
    user_uuid = add_user(user_id) if user_id else user_uuid
    tweet_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, str(tweet_id)))

    with DatabaseConnection() as cursor:
        if not get_tweet(tweet_uuid):
            cursor.execute(
                "INSERT INTO Tweets(TweetID, TweetUUID, UserUUID, TweetText, TweetMeta, TweetMedia, Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    tweet_id,
                    tweet_uuid,
                    user_uuid,
                    tweet_text,
                    json.dumps(tweet_meta),
                    json.dumps(tweet_media),
                    datetime.now()
                )
            )
    return tweet_uuid


def get_tweet(tweet_uuid=None, user_uuid=None):
    with DatabaseConnection() as cursor:
        if not tweet_uuid and not user_uuid:
            tweets = [i for i in cursor.execute("SELECT * FROM Tweets WHERE 1=1")]
        else:
            tweets = [i for i in cursor.execute("SELECT * FROM Tweets WHERE UserUUID=? OR TweetUUID=?", (user_uuid, tweet_uuid))] 
    return tweets


def delete_tweet(tweet_uuid=None, user_uuid=None):
    if not tweet_uuid and not user_uuid:
        return

    with DatabaseConnection() as cursor:
        cursor.execute("DELETE FROM Tweets WHERE UserUUID=? OR TweetUUID=?", (user_uuid, tweet_uuid))


# Media manipulation methods
def add_media(media_id, media_category, media_description, user_id=None, tweet_id=None, user_uuid=None, tweet_uuid=None):
    if (not user_id and not user_uuid) or (not tweet_uuid and not tweet_id):
        return
    user_uuid = add_user(user_id) if user_id else user_uuid
    media_uuid = str(uuid.uuid4())

    with DatabaseConnection() as cursor:
        if not get_media(tweet_uuid=tweet_id):
            cursor.execute(
                "INSERT INTO Media(MediaUUID, MediaID, UserUUID, TweetUUID, MediaCategory, MediaDescription) VALUES (?, ?, ?, ?, ?, ?)",
                (media_uuid, json.dumps(media_id), user_uuid, tweet_uuid, media_category, media_description))
    return media_uuid

def get_media(user_uuid=None, media_uuid=None, media_category=None, tweet_uuid=None):
    with DatabaseConnection() as cursor:
        media = [i for i in cursor.execute("""
        SELECT 
            MediaUUID,
            MediaID,
            MediaDescription,
            MediaCategory,
            u.*,
            t.*

        FROM Media AS m
        INNER JOIN Users AS u
            ON u.UserUUID = m.UserUUID
        INNER JOIN Tweets AS t
            ON t.TweetUUID = m.TweetUUID

        WHERE m.UserUUID=? OR m.MediaUUID=? OR m.MediaCategory=? OR m.TweetUUID=?""",
         (user_uuid, media_uuid, media_category, tweet_uuid))]
    return media


def delete_media(media_uuid=None, tweet_uuid=None, user_uuid=None):
    with DatabaseConnection() as cursor:
        cursor.execute("DELETE FROM Users WHERE UserUUID=? OR TweetUUID=? OR MediaUUID=?", (user_uuid,))

# Inclusion Queue manipulation methods
def add_request(user_id=None, user_uuid=None, tweet_uuid=None):
    if (not user_id and not user_uuid) or not tweet_uuid:
        return

    user_uuid = add_user(user_id) if user_id else user_uuid
    request_uuid = str(uuid.uuid4())

    with DatabaseConnection() as cursor:
        cursor.execute(
        "INSERT INTO RequestQueue(RequestUUID, TweetUUID, UserUUID) VALUES (?, ?, ?)",
        (request_uuid, tweet_uuid, user_uuid))

    return request_uuid


def get_request(request_uuid=None, user_uuid=None, user_id=None, tweet_id=None, tweet_uuid=None):
    if (not user_id and not user_uuid) and (not tweet_uuid and not tweet_id) and not request_uuid:
        return

    user_uuid = add_user(user_id) if user_id else user_uuid
    tweet_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, str(tweet_id))) if tweet_id else None
    print(request_uuid, user_uuid, tweet_uuid, tweet_id, user_id)
    output = []
    with DatabaseConnection() as cursor:
        cursor.execute(
        """SELECT
            r.RequestUUID,
            u.UserID,
            t.*
        FROM RequestQueue AS r
        INNER JOIN Tweets AS t
            ON t.TweetUUID = r.TweetUUID
        INNER JOIN Users as u
            ON u.UserUUID = r.UserUUID
        WHERE RequestUUID=? OR r.UserUUID=? or r.TweetUUID=?""",
        (request_uuid, user_uuid, tweet_uuid))
        output = [i for i in cursor]
    return output


def remove_request(request_uuid=None, user_uuid=None, user_id=None, tweet_id=None, tweet_uuid=None):
    if (not user_id and not user_uuid) or (not tweet_uuid and not tweet_id) or not request_uuid:
        return
    
    user_uuid = add_user(user_id) if not user_uuid else user_uuid
    tweet_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, str(tweet_id))) if not tweet_id else None

    with DatabaseConnection() as cursor:
        cursor.execute(
        "DELETE FROM RequestQueue WHERE RequestUUID=? OR TweetUUID=? OR UserUUID=?",
        (request_uuid, tweet_uuid, user_uuid))
