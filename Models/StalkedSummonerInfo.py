class StalkedSummonerInfo:
    def __init__(self, id=None, puuid=None, riot_name=None, tag_line=None, game_id=None, was_in_game=None,
                 consecutive_losses=None, consecutive_wins=None, time_wasted=None, summoner_id=None, total_wins=None,
                 total_losses=None, lp=None, rank=None, tier=None):
        self.id = id,
        self.puuid = puuid
        self.riot_name = riot_name
        self.tag_line = tag_line
        self.game_id = game_id
        self.was_in_game = was_in_game
        self.consecutive_losses = consecutive_losses
        self.consecutive_wins = consecutive_wins
        self.time_wasted = time_wasted
        self.summoner_id = summoner_id
        self.total_wins = total_wins
        self.total_losses = total_losses
        self.lp = lp
        self.rank = rank
        self.tier = tier

    @classmethod
    def from_database_row(cls, row):
        summoners = []
        for r in row:
            summoners.append(cls(*r))
        return summoners

    def __str__(self):
        return (f"Stalked Summoner Info:\n"
                f"ID: {self.id}\n"
                f"PUUID: {self.puuid}\n"
                f"Riot Name: {self.riot_name}\n"
                f"Tag Line: {self.tag_line}\n"
                f"Game ID: {self.game_id}\n"
                f"Was in Game: {self.was_in_game}\n"
                f"Consecutive Losses: {self.consecutive_losses}\n"
                f"Consecutive Wins: {self.consecutive_wins}\n"
                f"Time Wasted: {self.time_wasted}\n"
                f"Summoner ID: {self.summoner_id}\n"
                f"Total Wins: {self.total_wins}\n"
                f"Total Losses: {self.total_losses}\n"
                f"LP: {self.lp}\n"
                f"Rank: {self.rank}\n"
                f"Tier: {self.tier}")
