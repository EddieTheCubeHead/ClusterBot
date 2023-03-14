-- Note that name is pk because we can specify a role that should exist by adding its name here
-- We get ID from the discord snowflake so without a connection to the server we cannot know the id
-- On startup the bot will go through all roles in this table with no ID, and either map them to an
-- identically named role, or if no role with that name exists, create a new role with that name
CREATE TABLE IF NOT EXISTS Roles (
    Name VARCHAR(32) PRIMARY KEY,
    ID INTEGER,
    Colour INTEGER
);

INSERT INTO Roles (Name, Colour) VALUES ('Jäsen', 0xd52020);