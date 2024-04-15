import requests
import json
from config import riot_api_key, region, region_wide

player_tracking_info = {}


def get_summoner_puuid(game_name, tag_line):
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={riot_api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return None
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None


def get_current_game(puuid):
    url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={riot_api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["gameType"] == "MATCHED" and data["gameMode"] == "CLASSIC":
            return {"in_game": True, "gameId": data["gameId"]}
    except requests.exceptions.RequestException as e:
        print(f"Game could not be found or api failed")
        return {"in_game": False}
    except json.decoder.JSONDecodeError as e:
        print(f"Json decode error")
        return None


def currect_game(game, puuid):
    if game["gameType"] == "MATCHED":
        print(game["gameType"])
        print(game["gameId"])
        print(game['gameLength'])


def check_last_game(game_id, puuid):
    url = f"https://{region_wide}.api.riotgames.com/lol/match/v5/matches/NA1_{game_id}?api_key={riot_api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        game = response.json()

        summoner = find_participant_by_puuid(game, puuid)
        team_position = summoner['teamPosition']
        side = 'idk'
        gold_difference = get_gold_difference(game_id, puuid)
        if summoner['role'] == 'SUPPORT' or summoner['role'] == 'CARRY':
            team_position = summoner['role']
        if summoner['teamId'] == 100:
            side = 'Blue'
        elif summoner['teamId'] == 200:
            side = 'Red'

        if gold_difference > 0:
            gold_difference = f'+{gold_difference}'

        summoner_data = {
            'teamPosition': team_position,
            'championName': summoner['championName'],
            'deaths': summoner['deaths'],
            'kills': summoner['kills'],
            'assists': summoner['assists'],
            'damageDealt': summoner['totalDamageDealtToChampions'],
            'damageTaken': summoner['totalDamageTaken'],
            'wardsPlaced': summoner['wardsPlaced'],
            'minionKilled': summoner['totalMinionsKilled'] + summoner['totalEnemyJungleMinionsKilled'] + summoner[
                'totalAllyJungleMinionsKilled'],
            'damageBuildings': summoner['damageDealtToBuildings'],
            'goldEarned': summoner['goldEarned'],
            'side': side,
            'goldDifference': gold_difference,
            'duration': game['info']['gameDuration'],
        }
        return summoner['win'], summoner_data

    except requests.exceptions.RequestException as e:
        print(f"Error in check_last_game from Riot API: {e}")
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None


def find_participant_by_puuid(game, puuid):
    for participant in game['info']['participants']:
        if participant['puuid'] == puuid:
            return participant
    return None


# alternative name get_match_timeline
def get_gold_difference(game_id, puuid):
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
