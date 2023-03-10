CREATE TABLE IF NOT EXISTS Migrations (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    LastFile INTEGER NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS Users (
    ID INTEGER PRIMARY KEY,
    VerifiedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS EmailVerifications (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Code CHARACTER(6) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    UserID INTEGER,
    FOREIGN KEY (UserID) REFERENCES Users(ID) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS GuildVerifications (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Code CHARACTER(6) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CreatedBy INTEGER,
    FOREIGN KEY (CreatedBy) REFERENCES Users(ID) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS Polls (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CreatedBy INTEGER,
    Hash CHARACTER(128) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CreatedBy) REFERENCES Users(ID) ON UPDATE CASCADE ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS UserVote (
    UserID INTEGER,
    PollID INTEGER,
    Hash CHARACTER(128) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID, PollID),
    FOREIGN KEY (UserID) REFERENCES Users(ID) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (PollID) REFERENCES Polls(ID) ON UPDATE CASCADE ON DELETE CASCADE
);


-- No UpdatedAt because it might give away the identity of the vote
CREATE TABLE IF NOT EXISTS Option (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PollID INTEGER,
    Name VARCHAR(64) NOT NULL,
    Votes INTEGER DEFAULT 0,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
