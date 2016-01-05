-- Table definitions for the tournament project.

-- Remove any previous db present before running tests
DROP DATABASE IF EXISTS tournament;

-- create a db
CREATE DATABASE tournament;

-- connect to the database
\c tournament;

CREATE TABLE standings ( id SERIAL PRIMARY KEY,
                         name TEXT NOT NULL,
                         wins INTEGER DEFAULT 0,
                         matches INTEGER DEFAULT 0,
                         odd_win INTEGER DEFAULT 0);

-- view for get standings of players
CREATE OR REPLACE VIEW get_standings AS
    SELECT * from standings ORDER BY wins DESC;
