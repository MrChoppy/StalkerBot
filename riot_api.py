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
        print(f"Error in get_summoner_puuid from Riot API: {e}")
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
        #currect_game(data, puuid)
        if data["gameType"] == "MATCHED" and data["gameMode"] == "CLASSIC":
            return {"in_game": True, "gameId":data["gameId"]}
    except requests.exceptions.RequestException as e:
        return {"in_game": False}
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None

def currect_game(game, puuid):
    if game["gameType"] == "MATCHED":
        print(game["gameType"])
        print(game["gameId"])
        print(game['gameLength'])

def check_last_game(gameId, puuid):
    url = f"https://{region_wide}.api.riotgames.com/lol/match/v5/matches/NA1_{gameId}?api_key={riot_api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        game = response.json()

        summoner = find_participant_by_puuid(game, puuid)
        if summoner['win'] == True:
            return True, game['info']['gameDuration']
        else:
            return False, game['info']['gameDuration']

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