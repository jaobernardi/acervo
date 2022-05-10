import sqlite3

from . import config

tables = [
    """
    CREATE TABLE Tweeter(
        ID INTEGER,
        PRIMARY KEY(ID)
    )
    """,
    """
    CREATE TABLE Tweet(
        ID INTEGER,
        TweeterID INTEGER,
        PRIMARY KEY(ID),
        FOREIGN KEY(TweeterID)
            REFERENCES Tweeter(ID)
            ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Media(
        ID INTEGER,
        Category TEXT,
        Description TEXT,
        TweeterID INTEGER,
        TweetID INTEGER,
        PRIMARY KEY(ID),
        FOREIGN KEY(TweeterID)
            REFERENCES Tweeters(ID)
            ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Requests(
        ID TEXT(36),
        TweetID INTEGER,
        Category TEXT,
        Description TEXT,
        PRIMARY KEY(ID),
        FOREIGN KEY(TweeterID)
            REFERENCES Tweeters(ID)
            ON DELETE CASCADE
        
    )
    """,
]


class DatabaseConnection(object):
    def __enter__(self):
        self.connection = sqlite3.connect(config.get_database())
        return self.connection.cursor()
    
    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()
