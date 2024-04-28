import discord
from Riot.RiotApi import RiotApi
from Database.DatabaseManager import DatabaseManager
from Discord.DiscordMessenger import DiscordMessenger


class GameHandler:
    def __init__(self, bot, channel):
        self.bot = bot
        self.db = DatabaseManager()
        self.riot = RiotApi()
        self.channel = channel

    async def handle_game_result(self, stalked_summoner_info):
        player_game_data = await self.riot.check_last_game(stalked_summoner_info.game_id, stalked_summoner_info.puuid)
        if player_game_data is not None:

            if player_game_data.win:
                await GameHandler.handle_win(self, stalked_summoner_info, player_game_data)
            else:
                await GameHandler.handle_loss(self, stalked_summoner_info, player_game_data)
            await self.check_leaderboard(stalked_summoner_info, player_game_data)
            await self.db.set_game_id(stalked_summoner_info.puuid, None)

    async def handle_win(self, stalked_summoner_info, player_game_data):
        await DiscordMessenger.send_embed(
            title="VICTORY",
            description=f"{stalked_summoner_info.riot_name} won a game in {player_game_data.duration} minutes!!",
            color=discord.Color.green(),
            player_game_data=player_game_data,
            channel=self.channel
        )

        if await self.db.get_consecutive_losses(stalked_summoner_info.puuid) > 0:
            await self.db.set_consecutive_losses(stalked_summoner_info.puuid, 0)
            await self.db.set_time_wasted(stalked_summoner_info.puuid, 0)
            time_wasted = 0
        await self.db.set_consecutive_losses(stalked_summoner_info.puuid, 0)
        stalked_summoner_info.consecutive_wins += 1
        stalked_summoner_info.time_wasted += player_game_data.duration
        await self.db.set_time_wasted(stalked_summoner_info.puuid, stalked_summoner_info.time_wasted)
        await self.db.set_consecutive_wins(stalked_summoner_info.puuid, stalked_summoner_info.consecutive_wins)

        if stalked_summoner_info.consecutive_wins >= 3:
            await DiscordMessenger.send_embed(
                title="Win streak!",
                description=f"{stalked_summoner_info.riot_name} has won {stalked_summoner_info.consecutive_wins} games in a row!",
                color=discord.Color.green(),
                channel=self.channel
            )

    async def handle_loss(self, stalked_summoner_info, player_game_data):
        await DiscordMessenger.send_embed(
            title="DEFEAT",
            description=f"{stalked_summoner_info.riot_name} wasted {player_game_data.duration} minutes on a game just to lose",
            color=discord.Color.red(),
            player_game_data=player_game_data,
            channel=self.channel
        )
        if await self.db.get_consecutive_wins(stalked_summoner_info.puuid) > 0:
            await self.db.set_consecutive_wins(stalked_summoner_info.puuid, 0)
            await self.db.set_time_wasted(stalked_summoner_info.puuid, 0)
            stalked_summoner_info.time_wasted = 0
        await self.db.set_consecutive_wins(stalked_summoner_info.puuid, 0)

        stalked_summoner_info.time_wasted += player_game_data.duration
        stalked_summoner_info.consecutive_losses += 1
        await self.db.set_consecutive_losses(stalked_summoner_info.puuid, stalked_summoner_info.consecutive_losses)
        await self.db.set_time_wasted(stalked_summoner_info.puuid, stalked_summoner_info.time_wasted)

        if stalked_summoner_info.consecutive_losses >= 3:
            await DiscordMessenger.send_embed(
                title="Lose streak!",
                description=f"{stalked_summoner_info.riot_name} has lost {stalked_summoner_info.consecutive_losses} games in a row for a grand total of {stalked_summoner_info.time_wasted} minutes!",
                color=discord.Color.brand_red(),
                channel=self.channel
            )

    async def check_leaderboard(self, stalked_summoner_info, player_game_data):
        leaderboard_data = await self.db.get_leaderboard_data()

        await self.db.get_consecutive_losses(stalked_summoner_info.puuid)
        for record in leaderboard_data:
            if record.stat_name == 'kills' and player_game_data.kills > int(int(record.stat_value)):
                await self.record_beat(stalked_summoner_info, record, player_game_data.kills)
                await self.db.update_leaderboard('kills', stalked_summoner_info, player_game_data.kills)
            elif record.stat_name == 'deaths' and player_game_data.deaths > int(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.deaths)
                await self.db.update_leaderboard('deaths', stalked_summoner_info, player_game_data.deaths)
            elif record.stat_name == 'assists' and player_game_data.assists > int(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.assists)
                await self.db.update_leaderboard('assists', stalked_summoner_info, player_game_data.assists)
            elif record.stat_name == 'damage_dealt' and player_game_data.damage_dealt > int(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.damage_dealt)
                await self.db.update_leaderboard('damage_dealt', stalked_summoner_info, player_game_data.damage_dealt)
            elif record.stat_name == 'dpm' and float(player_game_data.dpm) > float(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.dpm)
                await self.db.update_leaderboard('dpm', stalked_summoner_info, player_game_data.dpm)
            elif record.stat_name == 'damage_taken' and player_game_data.damage_taken > int(record.stat_value):
                # await self.record_beat(stalked_summoner_info, record, player_game_data.damage_taken)
                await self.db.update_leaderboard('damage_taken', stalked_summoner_info, player_game_data.damage_taken)
            elif record.stat_name == 'wards_placed' and player_game_data.wards_placed > int(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.wards_placed)
                await self.db.update_leaderboard('wards_placed', stalked_summoner_info, player_game_data.wards_placed)
            elif record.stat_name == 'vision_score' and player_game_data.vision_score > int(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.vision_score)
                await self.db.update_leaderboard('vision_score', stalked_summoner_info, player_game_data.vision_score)
            elif record.stat_name == 'minions_killed' and player_game_data.minions_killed > int(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.minions_killed)
                await self.db.update_leaderboard('minions_killed', stalked_summoner_info,
                                                 player_game_data.minions_killed)
            elif record.stat_name == 'csm' and float(player_game_data.csm) > float(record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.csm)
                await self.db.update_leaderboard('csm', stalked_summoner_info, player_game_data.csm)
            elif record.stat_name == 'damage_buildings' and player_game_data.damage_buildings > int(record.stat_value):
                # await self.record_beat(stalked_summoner_info, record, player_game_data.damage_buildings)
                await self.db.update_leaderboard('damage_buildings', stalked_summoner_info,
                                                 player_game_data.damage_buildings)
            elif record.stat_name == 'gold_earned' and player_game_data.gold_earned > int(record.stat_value):
                # await self.record_beat(stalked_summoner_info, record, player_game_data.gold_earned)
                await self.db.update_leaderboard('gold_earned', stalked_summoner_info, player_game_data.gold_earned)
            elif record.stat_name == 'gold_difference_positive' and int(player_game_data.gold_difference) > int(
                    record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.gold_difference)
                await self.db.update_leaderboard('gold_difference_positive', stalked_summoner_info,
                                                 player_game_data.gold_difference)
            elif record.stat_name == 'gold_difference_negative' and int(player_game_data.gold_difference) < int(
                    record.stat_value):
                await self.record_beat(stalked_summoner_info, record, player_game_data.gold_difference)
                await self.db.update_leaderboard('gold_difference_negative', stalked_summoner_info,
                                                 player_game_data.gold_difference)
            elif record.stat_name == 'win_streak' and int(stalked_summoner_info.consecutive_wins) > int(
                    record.stat_value):
                await self.record_beat(stalked_summoner_info, record, stalked_summoner_info.consecutive_wins)
                await self.db.update_leaderboard('win_streak', stalked_summoner_info,
                                                 stalked_summoner_info.consecutive_wins)
            elif record.stat_name == 'lose_streak' and int(stalked_summoner_info.consecutive_losses) > int(
                    record.stat_value):
                await self.record_beat(stalked_summoner_info, record, stalked_summoner_info.consecutive_losses)
                await self.db.update_leaderboard('lose_streak', stalked_summoner_info,
                                                 stalked_summoner_info.consecutive_losses)

    async def record_beat(self, stalked_summoner_info, record, player_stat):

        if record.stat_name == 'gold_difference_positive':
            formatted_stat_name = 'GD@15+'
        elif record.stat_name == 'gold_difference_negative':
            formatted_stat_name = 'GD@15-'
        else:
            formatted_stat_name = " ".join(word.capitalize() for word in record.stat_name.split("_"))

        if record.summoner_id is not None:
            previous_summoner = await self.db.get_summoner_by_id(record.summoner_id)
            await DiscordMessenger.send_embed(
                title="Record beat!",
                description=f"{stalked_summoner_info.riot_name} has beaten the record for {formatted_stat_name} with {player_stat}! Was {record.stat_value} held by {previous_summoner[2]}.",
                color=discord.Color.purple(),
                channel=self.channel
            )
        else:
            await DiscordMessenger.send_embed(
                title="Record beat!",
                description=f"{stalked_summoner_info.riot_name} has beaten the record for {formatted_stat_name} with {player_stat}!.",
                color=discord.Color.purple(),
                channel=self.channel
            )
