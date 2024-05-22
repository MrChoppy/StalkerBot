class LeaderboardStat:
    def __init__(self, id, stat_name, summoner_id, stat_value, season_id):
        self.id = id
        self.stat_name = stat_name
        self.summoner_id = summoner_id
        self.stat_value = stat_value
        self.season_id = season_id

    def __repr__(self):
        return f"LeaderboardEntry(stat_name={self.stat_name}, summoner_id={self.summoner_id}, stat_value={self.stat_value})"
