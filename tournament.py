#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    try:
        con = connect()
        cur = con.cursor()
        cur.execute("DELETE FROM standings")
        con.commit()
        cur.close()
    except:
        print 'could not remove matches from the db'


def deletePlayers():
    """Remove all the player records from the database."""
    try:
        con = connect()
        cur = con.cursor()
        cur.execute("DELETE FROM standings")
        con.commit()
        cur.close()
    except:
        print 'could not remove players from the db'


def countPlayers():
    """Returns the number of players currently registered."""
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(name) FROM standings")
    players_tuple = cur.fetchone()
    try:
        players_count = int(players_tuple[0])
    except:
        return 0
    con.commit()
    cur.close()
    return players_count

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    try:
        con = connect()
        cur = con.cursor()
        cur.execute ("INSERT INTO standings (name) VALUES (%s)", (name,))
        con.commit()
        cur.close()
    except:
        print 'could not add player %s to the db' % (name,)

def playerStandings(include_odd_win=None):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    If there are odd number of players, then pick a random player
    for odd win and return the standings of the players

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        include_odd_win: if this is set to 1, it will return all the player
        standings including player with odd win
    """
    con = connect()
    cur = con.cursor()
    players_count = countPlayers()
    cur.execute("SELECT * from get_standings")
    rows = cur.fetchall()
    # Check if there are odd players
    if players_count % 2 != 0:
        # Get a list of players who did not win previously
        cur.execute("SELECT * from standings where odd_win=0")
        rows_for_odd_win = cur.fetchall()
        # Pick a random player from list of players who did not win previously
        winning_player = random.choice(rows_for_odd_win)
        winning_player_id = winning_player[0]
        reportMatch(winner = winning_player_id,
                    odd_win = 1)
        # Remove the odd player from the list of current players
        rows.remove(winning_player)

    # If we need to return all the players with odd_win, then fetch
    # the db again
    if include_odd_win:
        cur.execute("SELECT * from get_standings")
        rows = cur.fetchall()
    cur.close()
    return rows

def reportMatch(winner,
                loser=None,
                odd_win=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost (optional in case of odd_win)
      odd_win: if this is set, it will process odd winner
    """
    con = connect()
    cur = con.cursor()
    # Update standings with num of wins and matches
    if odd_win:
        cur.execute ("UPDATE standings SET wins = wins + 1,\
                                           matches = matches + 1,\
                                           odd_win = odd_win + 1\
                                           WHERE id = %s", [winner])
    else:
        cur.execute ("UPDATE standings SET wins = wins + 1,\
                                       matches = matches + 1\
                                       WHERE id = %s", [winner])
        cur.execute ("UPDATE standings SET matches = matches + 1\
                                       WHERE id = %s", [loser])
    con.commit()
    cur.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id, name from standings WHERE odd_win = 0 ORDER BY wins")
    rows = cur.fetchall()
    # Get the pairs of players from the list fetched from db
    pairs = [(rows[i] + rows[i+1]) for i in range(0,len(rows),2)]
    cur.close()
    return pairs
