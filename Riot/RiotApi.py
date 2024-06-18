import json
import aiohttp

from Models.PlayerGameData import PlayerGameData
from Models.StalkedSummonerInfo import StalkedSummonerInfo
from config import riot_api_key, region, region_wide


class RiotApi:
    def __init__(self):
        pass

    async def get_summoner(self, riot_name, tag_line):
        puuid = await self.get_summoner_puuid(riot_name, tag_line)
        if puuid:
            summoner_id = await self.get_summoner_id(puuid)
            return StalkedSummonerInfo(puuid=puuid, riot_name=riot_name,
                                       tag_line=tag_line, summoner_id=summoner_id)

    async def get_summoner_puuid(self, riot_name, tag_line):
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_name}/{tag_line}?api_key={riot_api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data['puuid']
        except aiohttp.ClientError as e:
            return None
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    async def get_summoner_id(self, puuid):
        url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={riot_api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data['id']
        except aiohttp.ClientError as e:
            return None
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    async def get_current_game(self, puuid):
        url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={riot_api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data["gameQueueConfigId"] == 420:
                        return data
        except aiohttp.ClientError as e:
            return None

    async def check_last_game(self, game_id, puuid):
        url = f"https://{region_wide}.api.riotgames.com/lol/match/v5/matches/NA1_{game_id}?api_key={riot_api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    game = await response.json()

            index, summoner = await self.find_participant_by_puuid(game, puuid)
            team_position = ''

            if index == 0 or index == 5:
                team_position = 'Top'
            elif index == 1 or index == 6:
                team_position = 'Jungle'
            elif index == 2 or index == 7:
                team_position = 'Mid'
            elif index == 3 or index == 8:
                team_position = 'Adc'
            elif index == 4 or index == 9:
                team_position = 'Support'

            side = 'idk'
            gold_difference = await self.get_gold_difference(game_id, puuid)

            if summoner['teamId'] == 100:
                side = 'Blue'
            elif summoner['teamId'] == 200:
                side = 'Red'

            if gold_difference > 0:
                gold_difference = f'+{gold_difference}'

            minions_killed = summoner['totalMinionsKilled'] + summoner['neutralMinionsKilled']

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
                vision_score=summoner['visionScore'],
                minions_killed=minions_killed,
                csm="{:.2f}".format(minions_killed / duration),
                damage_buildings=summoner['damageDealtToBuildings'],
                gold_earned=summoner['goldEarned'],
                side=side,
                gold_difference=gold_difference,
                duration=duration,
                win=summoner['win']
            )

        except aiohttp.ClientError as e:
            print(f"Error in check_last_game from Riot API: {e}")

    async def find_participant_by_puuid(self, game, puuid):
        for index, participant in enumerate(game['info']['participants']):
            if participant['puuid'] == puuid:
                return index, participant
        return None, None

    async def get_gold_difference(self, game_id, puuid):
        try:
            url = f'https://{region_wide}.api.riotgames.com/lol/match/v5/matches/NA1_{game_id}/timeline?api_key={riot_api_key}'

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    timeline_data = await response.json()

            timeline_data = timeline_data['info']

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

    async def get_player_ranked_info(self, stalked_summoner_info):
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{stalked_summoner_info.summoner_id}?api_key={riot_api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    for queue in data:
                        if queue['queueType'] == 'RANKED_SOLO_5x5':
                            return StalkedSummonerInfo(id=stalked_summoner_info.id,
                                                       puuid=stalked_summoner_info.puuid,
                                                       riot_name=stalked_summoner_info.riot_name,
                                                       tag_line=stalked_summoner_info.tag_line,
                                                       game_id=stalked_summoner_info.game_id,
                                                       was_in_game=stalked_summoner_info.was_in_game,
                                                       time_wasted=stalked_summoner_info.time_wasted,
                                                       consecutive_wins=stalked_summoner_info.consecutive_wins,
                                                       consecutive_losses=stalked_summoner_info.consecutive_losses,
                                                       summoner_id=stalked_summoner_info.summoner_id,
                                                       total_wins=queue['wins'],
                                                       total_losses=queue['losses'],
                                                       lp=queue['leaguePoints'],
                                                       rank=queue['rank'],
                                                       tier=queue['tier'])
        except aiohttp.ClientError as e:
            return None
