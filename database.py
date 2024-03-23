import sqlite3

conn = sqlite3.connect('summoners.db')
c = conn.cursor()

def initialize_database():
    initialize()


def initialize():
    c.execute('''
        CREATE TABLE IF NOT EXISTS summoners (
            puuid TEXT,
            game_name TEXT,
            tag_line TEXT,
            game_id INTEGER DEFAULT NULL,
            was_in_game BOOLEAN DEFAULT FALSE,
            consecutive_losses INTEGER DEFAULT 0,
            consecutive_wins INTEGER DEFAULT 0,
            time_wasted INTEGER DEFAULT 0
        )
    ''')
    conn.commit()


def insert_summoner(puuid, game_name, tag_line):
    c.execute("INSERT INTO summoners (puuid, game_name, tag_line) VALUES (?, ?, ?)", (puuid, game_name, tag_line))
    conn.commit()


def close_connection():
    global conn
    if conn:
        conn.close()


def get_summoner(game_name, tag_line):
    game_name_clean = game_name.replace(" ", "").lower()
    tag_line_clean = tag_line.replace(" ", "").lower()

    c.execute(
        "SELECT game_name, tag_line, puuid FROM summoners WHERE LOWER(REPLACE(game_name, ' ', ''))=? AND LOWER(REPLACE(tag_line, ' ', ''))=?",
        (game_name_clean, tag_line_clean))
    result = c.fetchone()
    if result:
        original_game_name, tag_line, puuid = result
        return original_game_name, tag_line, puuid
    else:
        return None



def delete_summoner(puuid):
    c.execute("DELETE FROM summoners WHERE puuid=?", (puuid,))
    conn.commit()


def set_game_id(puuid, gameId):
    c.execute("UPDATE summoners SET game_id=? WHERE puuid=?", (gameId, puuid))
    conn.commit()


def get_game_id(puuid):
    c.execute("SELECT game_id FROM summoners WHERE puuid=?", (puuid,))
    return c.fetchone()[0]


def set_was_in_game(puuid, was_in_game):
    c.execute("UPDATE summoners SET was_in_game=? WHERE puuid=?", (was_in_game, puuid))
    conn.commit()


def get_was_in_game(puuid):
    c.execute("SELECT was_in_game FROM summoners WHERE puuid=?", puuid)
    return c.fetchone()[0]


def get_all_summoners():
    c.execute("SELECT puuid, game_name, tag_line, game_id, was_in_game, consecutive_losses, consecutive_wins, time_wasted FROM summoners")
    return c.fetchall()


def set_consecutive_losses(puuid, consecutive_losses):
    c.execute("UPDATE summoners SET consecutive_losses=? WHERE puuid=?", (consecutive_losses, puuid))
    conn.commit()


def set_time_wasted(puuid, time_wasted):
    c.execute("UPDATE summoners SET time_wasted=? WHERE puuid=?", (time_wasted, puuid))
    conn.commit()


def set_consecutive_wins(puuid, consecutive_wins):
    c.execute("UPDATE summoners SET consecutive_wins=? WHERE puuid=?", (consecutive_wins, puuid))
    conn.commit()
