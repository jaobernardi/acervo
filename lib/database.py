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
        `UserID` INT(36)
    )
    """

    tweets = """
    CREATE TABLE Tweets (
        `TweetID` INT(36),
        `UserID` TEXT(36),
        `TweetText` TEXT(290),
        `TweetMeta` MEDIUMTEXT,
        `TweetMedia` TEXT(128),
        `Timestamp` DATETIME,
        FOREIGN KEY(UserID) REFERENCES Users(UserID)
    )
    """

    media = """
    CREATE TABLE Media (
        `MediaUUID` TEXT(36),
        `MediaID` INT(36),        
        `UserID` TEXT(36),
        `TweetID` TEXT(36),
        `MediaCategory` TEXT,
        `MediaDescription` TEXT,
        FOREIGN KEY(UserID) REFERENCES Users(UserID),
        FOREIGN KEY(TweetID) REFERENCES Tweets(TweetID)
    )
    """

    inclusion_queue = """
    CREATE TABLE RequestQueue (
        `RequestUUID` TEXT(36),
        `Status` TEXT(16),
        `TweetID` TEXT(36),
        `UserID` TEXT(36),
        FOREIGN KEY(UserID) REFERENCES Users(UserID),
        FOREIGN KEY(TweetID) REFERENCES Tweets(TweetID)
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
    with DatabaseConnection() as cursor:
        if not get_user(user_id):
            cursor.execute("INSERT INTO Users(UserID) VALUES (?)", (user_id,))



def get_user(user_id=None):
    with DatabaseConnection() as cursor:
        if not user_id:
             user = [i for i in cursor.execute("SELECT * FROM Users WHERE 1=1")]
        else:
            user = [i for i in cursor.execute("SELECT * FROM Users WHERE UserID=?", (user_id,))]
    return user[0] if len(user) == 1 else user


def delete_user(user_id):
    with DatabaseConnection() as cursor:
        cursor.execute("DELETE FROM Users WHERE UserID=?", (user_id,))


# Tweet manipulation methods
def add_tweet(tweet_id, tweet_text, tweet_meta, tweet_media, user_id=None):
    if not user_id:
        return    
    add_user(user_id)
    with DatabaseConnection() as cursor:
        if not get_tweet(tweet_id):
            cursor.execute(
                "INSERT INTO Tweets(TweetID, UserID, TweetText, TweetMeta, TweetMedia, Timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    tweet_id,
                    user_id,
                    tweet_text,
                    json.dumps(tweet_meta),
                    json.dumps(tweet_media),
                    datetime.now()
                )
            )


def get_tweet(tweet_id=None, user_id=None):
    if user_id:
        add_user(user_id)
    with DatabaseConnection() as cursor:
        if not tweet_id and not user_id:
            tweets = [i for i in cursor.execute("SELECT * FROM Tweets WHERE 1=1")]
        else:
            tweets = [i for i in cursor.execute("SELECT * FROM Tweets WHERE UserID=? OR TweetID=?", (user_id, tweet_id))] 
    return tweets


def delete_tweet(tweet_id=None, user_id=None):
    if not tweet_id and not user_id:
        return
    if user_id:
        add_user(user_id)
    with DatabaseConnection() as cursor:
        cursor.execute("DELETE FROM Tweets WHERE UserID=? OR TweetID=?", (user_id, tweet_id))


# Media manipulation methods
def add_media(media_id, media_category, media_description, user_id=None, tweet_id=None):
    if not user_id or not tweet_id:
        return
    if user_id:
        add_user(user_id)
    media_uuid = str(uuid.uuid4())

    with DatabaseConnection() as cursor:
        if not get_media(tweet_id=tweet_id):
            cursor.execute(
                "INSERT INTO Media(MediaUUID, MediaID, UserID, TweetID, MediaCategory, MediaDescription) VALUES (?, ?, ?, ?, ?, ?)",
                (media_uuid, json.dumps(media_id), user_id, tweet_id, media_category, media_description))
    return media_uuid

def get_media(user_id=None, media_uuid=None, media_category=None, tweet_id=None):
    if user_id:
        add_user(user_id)
    with DatabaseConnection() as cursor:
        if not user_id and not media_uuid and not media_category and not tweet_id:
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
                ON u.UserID = m.UserID
            INNER JOIN Tweets AS t
                ON t.TweetID = m.TweetID

            WHERE 1=1""",
            )]
        else:
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
                ON u.UserID = m.UserID
            INNER JOIN Tweets AS t
                ON t.TweetID = m.TweetID

            WHERE m.UserID=? OR m.MediaUUID=? OR m.MediaCategory=? OR m.TweetID=?""",
            (user_id, media_uuid, media_category, tweet_id))]
    return media


def delete_media(media_uuid=None, tweet_id=None, user_id=None):
    with DatabaseConnection() as cursor:
        cursor.execute("DELETE FROM Media WHERE UserID=? OR TweetID=? OR MediaUUID=?", (user_id, tweet_id, media_uuid))

# Inclusion Queue manipulation methods
def add_request(user_id=None, tweet_id=None, status="Pendente"):
    if not user_id or not tweet_id:
        return
    if user_id:
        add_user(user_id)
    
    if req := get_request(tweet_id=tweet_id):
        return req[0][0]

    request_uuid = str(uuid.uuid4())

    with DatabaseConnection() as cursor:
        cursor.execute(
        "INSERT INTO RequestQueue(RequestUUID, Status, TweetID, UserID) VALUES (?, ?, ?, ?)",
        (request_uuid, status, tweet_id, user_id))

    return request_uuid


def edit_request(request_uuid, status):
    with DatabaseConnection() as cursor:
        cursor.execute(
        "UPDATE RequestQueue SET Status = ? WHERE RequestUUID = ?",
        (status, request_uuid))


def get_request(request_uuid=None, user_id=None, tweet_id=None):

    if user_id:
        add_user(user_id)

    output = []
    with DatabaseConnection() as cursor:
        if not user_id and not tweet_id and not request_uuid:
            cursor.execute(
            """SELECT
                r.RequestUUID,
                r.Status,
                t.*
            FROM RequestQueue AS r
            INNER JOIN Tweets AS t
                ON t.TweetID = r.TweetID
            WHERE 1=1""",
            )
        else:
            cursor.execute(
            """SELECT
                r.RequestUUID,
                r.Status,
                t.*
            FROM RequestQueue AS r
            INNER JOIN Tweets AS t
                ON t.TweetID = r.TweetID
            WHERE RequestUUID=? OR r.UserID=? or r.TweetID=?""",
            (request_uuid, user_id, tweet_id))
        output = [i for i in cursor]
    return output


def remove_request(request_uuid=None, user_id=None, tweet_id=None):
    if not user_id and not tweet_id and not request_uuid:
        return
    if user_id:
        add_user(user_id)
    with DatabaseConnection() as cursor:
        cursor.execute(
        "DELETE FROM RequestQueue WHERE RequestUUID=? OR TweetID=? OR UserID=?",
        (request_uuid, tweet_id, user_id))

def clear_requests():
    with DatabaseConnection() as cursor:
        cursor.execute(
        "DELETE FROM RequestQueue WHERE 1=1")