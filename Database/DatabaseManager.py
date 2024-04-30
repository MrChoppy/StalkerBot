import sqlite3

from Models.LeaderboardStat import LeaderboardStat
from Models.StalkedSummonerInfo import StalkedSummonerInfo


class DatabaseManager:
    def __init__(self, database_name='summoners.db'):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    async def initialize_database(self):
        await self.initialize()

    async def initialize(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS summoner_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puuid TEXT,
                game_name TEXT,
                tag_line TEXT,
                game_id INTEGER DEFAULT NULL,
                was_in_game BOOLEAN DEFAULT FALSE,
                consecutive_losses INTEGER DEFAULT 0,
                consecutive_wins REAL DEFAULT 0,
                time_wasted INTEGER DEFAULT 0,
                summoner_id TEXT,
                total_wins INTEGER,
                total_losses INTEGER,
                lp INTEGER,
                rank TEXT,
                tier TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY,
                stat_name TEXT,
                summoner_id INTEGER,
                stat_value INTEGER,
                FOREIGN KEY (summoner_id) REFERENCES summoner_data (id)
            )
        ''')
        self.connection.commit()

    async def insert_summoner(self, stalked_summoner):
        self.cursor.execute("INSERT INTO summoner_data (puuid, game_name, tag_line, summoner_id) VALUES (?, ?, ?, ?)",
                            (stalked_summoner.puuid, stalked_summoner.riot_name, stalked_summoner.tag_line,
                             stalked_summoner.summoner_id))
        self.connection.commit()

    async def close_connection(self):
        if self.connection:
            self.connection.close()

    async def get_summoner(self, game_name, tag_line):
        riot_name_clean = game_name.replace(" ", "").lower()
        tag_line_clean = tag_line.replace(" ", "").lower()

        self.cursor.execute(
            "SELECT id, game_name, tag_line, puuid FROM summoner_data WHERE LOWER(REPLACE(game_name, ' ', ''))=? AND "
            "LOWER("
            "REPLACE(tag_line, ' ', ''))=?",
            (riot_name_clean, tag_line_clean))
        result = self.cursor.fetchone()
        if result:
            id, original_riot_name, tag_line, puuid = result
            return StalkedSummonerInfo(id=id, puuid=puuid, riot_name=original_riot_name, tag_line=tag_line)
        else:
            return None

    async def get_summoner_by_puuid(self, puuid):
        summoner = self.cursor.execute("SELECT id FROM summoner_data WHERE puuid=?", (puuid,)).fetchone()
        if summoner:
            return summoner
        else:
            return None

    async def get_summoner_by_id(self, id):
        summoner = self.cursor.execute("SELECT * FROM summoner_data WHERE id=?", (id,)).fetchone()
        if summoner:
            return summoner
        else:
            return None

    async def delete_summoner(self, puuid):
        self.cursor.execute("DELETE FROM summoner_data WHERE puuid=?", (puuid,))
        self.connection.commit()

    async def set_game_id(self, puuid, game_id):
        self.cursor.execute("UPDATE summoner_data SET game_id=? WHERE puuid=?", (game_id, puuid))
        self.connection.commit()

    async def get_game_id(self, puuid):
        self.cursor.execute("SELECT game_id FROM summoner_data WHERE puuid=?", (puuid,))
        return self.cursor.fetchone()[0]

    async def set_was_in_game(self, puuid, was_in_game):
        self.cursor.execute("UPDATE summoner_data SET was_in_game=? WHERE puuid=?", (was_in_game, puuid))
        self.connection.commit()

    async def get_was_in_game(self, puuid):
        self.cursor.execute("SELECT was_in_game FROM summoner_data WHERE puuid=?", puuid)
        return self.cursor.fetchone()[0]

    async def get_all_summoners(self):
        self.cursor.execute("SELECT * FROM summoner_data")
        rows = self.cursor.fetchall()
        return [StalkedSummonerInfo(*row) for row in rows]

    async def get_summoner_info_from_puuid(self, puuid):
        self.cursor.execute(
            "SELECT * FROM summoner_data WHERE puuid = ?", (puuid,))
        row = self.cursor.fetchone()
        if row:
            return StalkedSummonerInfo(*row)
        else:
            return None

    async def set_consecutive_losses(self, puuid, consecutive_losses):
        self.cursor.execute("UPDATE summoner_data SET consecutive_losses=? WHERE puuid=?", (consecutive_losses, puuid))
        self.connection.commit()

    async def get_consecutive_losses(self, puuid):
        self.cursor.execute("SELECT consecutive_losses FROM summoner_data WHERE puuid=?", (puuid,))
        return self.cursor.fetchone()[0]

    async def set_consecutive_wins(self, puuid, consecutive_wins):
        self.cursor.execute("UPDATE summoner_data SET consecutive_wins=? WHERE puuid=?", (consecutive_wins, puuid))
        self.connection.commit()

    async def get_consecutive_wins(self, puuid):
        self.cursor.execute("SELECT consecutive_wins FROM summoner_data WHERE puuid=?", (puuid,))
        return self.cursor.fetchone()[0]

    async def set_time_wasted(self, puuid, time_wasted):
        self.cursor.execute("UPDATE summoner_data SET time_wasted=? WHERE puuid=?", (time_wasted, puuid))
        self.connection.commit()

    async def get_leaderboard_data(self):
        try:
            self.cursor.execute("SELECT * FROM leaderboard")
            rows = self.cursor.fetchall()
            leaderboard_data = []
            ignored_data = ['damage_taken', 'damage_buildings', 'gold_earned']
            for row in rows:
                id, stat_name, summoner_id, stat_value = row
                if stat_name not in ignored_data:
                    stat = LeaderboardStat(id, stat_name, summoner_id, stat_value)
                    leaderboard_data.append(stat)
            return leaderboard_data
        except Exception as e:
            print(f"Error retrieving leaderboard data: {e}")
            return None

    async def update_leaderboard(self, stat_name, summoner_info, stat_value):
        summoner = await self.get_summoner_by_puuid(summoner_info.puuid)

        self.cursor.execute("UPDATE leaderboard SET summoner_id=?, stat_value=? WHERE stat_name=?",
                            (summoner[0], stat_value, stat_name))
        self.connection.commit()

    async def set_summoner_id(self, puuid, summoner_id):
        self.cursor.execute("UPDATE summoner_data SET summoner_id=? WHERE puuid=?", (summoner_id, puuid))
        self.connection.commit()
