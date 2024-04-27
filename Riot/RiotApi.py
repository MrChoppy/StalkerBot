import json
import requests
from Models.PlayerGameData import PlayerGameData
from Models.StalkedSummoner import StalkedSummoner
from config import riot_api_key, region, region_wide


class RiotApi:
    def __init__(self):
        pass

    async def get_summoner_puuid(self, game_name, tag_line):
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={riot_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return StalkedSummoner(puuid=data['puuid'], riot_name=data['gameName'], tag_line=data['tagLine'])
        except requests.exceptions.RequestException as e:
            return None
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    async def get_current_game(self, puuid):
        url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={riot_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["gameQueueConfigId"] == 420:
                return data
        except requests.exceptions.RequestException as e:
            return None

    async def check_last_game(self, game_id, puuid):
        url = f"https://{region_wide}.api.riotgames.com/lol/match/v5/matches/NA1_{game_id}?api_key={riot_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            game = response.json()

            summoner = await self.find_participant_by_puuid(game, puuid)
            team_position = summoner['teamPosition']
            side = 'idk'
            gold_difference = await self.get_gold_difference(game_id, puuid)
            if summoner['role'] == 'SUPPORT' or summoner['role'] == 'CARRY':
                team_position = summoner['role']
            if summoner['teamId'] == 100:
                side = 'Blue'
            elif summoner['teamId'] == 200:
                side = 'Red'

            if gold_difference > 0:
                gold_difference = f'+{gold_difference}'
            minions_killed = summoner['totalMinionsKilled'] + summoner['totalEnemyJungleMinionsKilled'] + summoner[
                'totalAllyJungleMinionsKilled']
            duration = game['info']['gameDuration'] // 60
            return PlayerGameData(
                team_position=team_position,
                champion_name=summoner['championName'],
                deaths=summoner['deaths'],
                kills=summoner['kills'],
                assists=summoner['assists'],
                damage_dealt=summoner['totalDamageDealtToChampions'],
                dpm="{:.2f}".format(summoner['totalDamageDealtToChampions'] / duration),
                damage_taken=summoner['totalDamageTaken'],
                wards_placed=summoner['wardsPlaced'],
                minions_killed=minions_killed,
                csm="{:.2f}".format(minions_killed / duration),
                damage_buildings=summoner['damageDealtToBuildings'],
                gold_earned=summoner['goldEarned'],
                side=side,
                gold_difference=gold_difference,
                duration=duration,
                win=summoner['win']
            )

        except requests.exceptions.RequestException as e:
            print(f"Error in check_last_game from Riot API: {e}")

    async def find_participant_by_puuid(self, game, puuid):
        for participant in game['info']['participants']:
            if participant['puuid'] == puuid:
                return participant
        return None

    async def get_gold_difference(self, game_id, puuid):
        try:
            url = f'https://{region_wide}.api.riotgames.com/lol/match/v5/matches/NA1_{game_id}/timeline?api_key={riot_api_key}'

            response = requests.get(url)
            response.raise_for_status()

            timeline_data = response.json()['info']

            main_player = 0
            opponent_player = 0
            gold_difference = 0
            for participant in timeline_data['participants']:
                if participant['puuid'] == puuid:
                    main_player = participant['participantId']
                    if main_player > 5:
                        opponent_player = main_player - 5
                    elif main_player <= 5:
                        opponent_player = main_player + 5

            for frame in timeline_data['frames']:
                if frame['timestamp'] >= 900000:
                    gold_difference = frame['participantFrames'][str(main_player)]['totalGold'] - \
                                      frame['participantFrames'][str(opponent_player)]['totalGold']
                    break
            return gold_difference

        except Exception as e:
            print("Error in gold difference: ", e)
            return 0
