SQLite format 3   @     
                                                               
 .O}   
� �T��
�                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 �%%�qtableRequestQueueRequestQueueCREATE TABLE RequestQueue (
        `RequestUUID` TEXT(36),
        `TweetUUID` TEXT(36),
        `UserUUID` TEXT(36),
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID),
        FOREIGN KEY(TweetUUID) REFERENCES Tweets(TweetUUID)
    )�K!!�atableStatisticsStatisticsCREATE TABLE Statistics (
        `UserUUID` TEXT(36),
        `TweetUUID` TEXT(36),
        `MediaUUID` TEXT(36),
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID),
        FOREIGN KEY(TweetUUID) REFERENCES Tweets(TweetUUID),
        FOREIGN KEY(MediaUUID) REFERENCES Media(MediaUUID)
    )�b�#tableMediaMediaCREATE TABLE Media (
        `MediaUUID` TEXT(36),
        `MediaID` INT(36),        
        `UserUUID` TEXT(36),
        `TweetUUID` TEXT(36),
        `MediaCategory` TEXT,
        `MediaDescription` TEXT,
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID),
        FOREIGN KEY(TweetUUID) REFERENCES Tweets(TweetUUID)
    )�@�[tableTweetsTweetsCREATE TABLE Tweets (
        `TweetID` INT(36),
        `TweetUUID` TEXT(36),
        `UserUUID` TEXT(36),
        `TweetText` TEXT(290),
        `TweetMeta` MEDIUMTEXT,
        `TweetMedia` TEXT(128),
        `Timestamp` DATETIME,
        FOREIGN KEY(UserUUID) REFERENCES Users(UserUUID)
    )g�-tableUsersUsersCREATE TABLE Users (
        `UserID` INT(36),
        `UserUUID` TEXT(36)
    )   � ��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ' Ubd5a1e79-468e-3424-b0cd-4a5910635e93'Uc8e1eb22-a627-3daa-884c-2205cf78d075   l l                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  �	UU!)+A9311744c-3746-3502-84c9-d06e8b5ea2d6c8e1eb22-a627-3daa-884c-2205cf78d075tweet text["tweet_meta"]["tweet_media"]2022-03-02 19:28:24.031815   } }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   � UUU22ac3fb1-42ca-44a0-a38f-826cf1daecdec8e1eb22-a627-3daa-884c-2205cf78d0759311744c-3746-3502-84c9-d06e8b5ea2d6BBBCategoria                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    pUUUa30eee08-61fe-4c64-a098-5d3939f156be9311744c-3746-3502-84c9-d06e8b5ea2d6c8e1eb22-a627-3daa-884c-2205cf78d075