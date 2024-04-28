class PlayerGameData:
    def __init__(self, team_position, champion_name, deaths, kills, assists, damage_dealt, dpm, damage_taken,
                 wards_placed, vision_score, minions_killed, csm, damage_buildings, gold_earned, side, gold_difference,
                 duration, win):
        self.team_position = team_position
        self.champion_name = champion_name
        self.deaths = deaths
        self.kills = kills
        self.assists = assists
        self.damage_dealt = damage_dealt
        self.dpm = dpm
        self.damage_taken = damage_taken
        self.wards_placed = wards_placed
        self.minions_killed = minions_killed
        self.vision_score = vision_score
        self.csm = csm
        self.damage_buildings = damage_buildings
        self.gold_earned = gold_earned
        self.side = side
        self.gold_difference = gold_difference
        self.duration = duration
        self.win = win
