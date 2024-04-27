class StalkedSummonerInfo:
    def __init__(self, id, puuid, riot_name, tag_line, game_id, was_in_game, consecutive_losses, consecutive_wins,
                 time_wasted):
        self.id = id,
        self.puuid = puuid
        self.riot_name = riot_name
        self.tag_line = tag_line
        self.game_id = game_id
        self.was_in_game = was_in_game
        self.consecutive_losses = consecutive_losses
        self.consecutive_wins = consecutive_wins
        self.time_wasted = time_wasted

    @classmethod
    def from_database_row(cls, row):
        summoners = []
        for r in row:
            summoners.append(cls(*r))
        return summoners
