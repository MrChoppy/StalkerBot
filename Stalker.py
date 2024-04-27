import discord
from discord.ext import commands, tasks
from Database.DatabaseManager import DatabaseManager
from Discord.DiscordMessenger import DiscordMessenger
from Game.GameHandler import GameHandler
from Models.StalkedSummonerInfo import StalkedSummonerInfo
from Riot.RiotApi import RiotApi


class Stalker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.db = DatabaseManager()
        self.riot = RiotApi()

    @commands.command()
    async def stalk(self, ctx, *args):
        for arg in args:
            if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
                await DiscordMessenger.send_message(
                    message="Invalid summoner name, must be in this format (no spaces): example#na1",
                    channel=self.channel)
                return
            game_name, tag_line = arg.split("#")

            stalked_summoner = await self.db.get_summoner(game_name, tag_line)
            if stalked_summoner:
                await DiscordMessenger.send_embed(
                    title="Sitting in a bush",
                    description=f"Now stalking {stalked_summoner.riot_name}#{stalked_summoner.tag_line}",
                    color=discord.Color.dark_embed(),
                    channel=self.channel
                )
            else:
                stalked_summoner = await self.riot.get_summoner_puuid(game_name, tag_line)
                if stalked_summoner:
                    await self.db.insert_summoner(stalked_summoner)
                    await DiscordMessenger.send_embed(
                        title="Sitting in a bush",
                        description=f"Now stalking {stalked_summoner.riot_name}#{stalked_summoner.tag_line}",
                        color=discord.Color.dark_embed(),
                        channel=self.channel
                    )
                else:
                    await DiscordMessenger.send_message(
                        message=f"Failed to find summoner with name {game_name}#{tag_line}",
                        channel=self.channel)

    @commands.command()
    async def unstalk(self, ctx, *args):
        for arg in args:
            if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
                await DiscordMessenger.send_message(
                    message="Invalid summoner name, must be in this format (no spaces): example#na1",
                    channel=self.channel)
                return
            riot_name, tag_line = arg.split("#")

            stalked_summoner = await self.db.get_summoner(riot_name, tag_line)
            if stalked_summoner:
                await DiscordMessenger.send_embed(
                    title="Out of the bush",
                    description=f"Stopped stalking {stalked_summoner.riot_name}#{stalked_summoner.tag_line}",
                    color=discord.Color.dark_embed(),
                    channel=self.channel
                )
                await self.db.delete_summoner(stalked_summoner.puuid)

            else:
                await DiscordMessenger.send_embed(
                    title="Who?",
                    description=f"You're not currently stalking {riot_name}#{tag_line}",
                    color=discord.Color.dark_embed(),
                    channel=self.channel
                )

    @commands.command()
    async def stalklist(self, ctx):
        stalked_players = await self.db.get_all_summoners()

        if stalked_players:
            embed_title = "Stalk List"
            embed_description = ""
            embed_color = discord.Color.green()

            for stalked_player in stalked_players:
                embed_description += f"**{stalked_player.riot_name}#{stalked_player.tag_line}**\n"

            await DiscordMessenger.send_embed(embed_title, embed_description, embed_color, channel=self.channel)
        else:
            await DiscordMessenger.send_embed("Stalk List", "No players are currently being stalked.",
                                              discord.Color.red(),
                                              channel=self.channel)

    @commands.command()
    async def leaderboard(self, ctx):
        leaderboard_data = await self.db.get_leaderboard_data()
        if leaderboard_data:
            embed = discord.Embed(title="Leaderboard", color=discord.Color.blue())
            for record in leaderboard_data:
                if record.summoner_id is not None and record.stat_name is not None:
                    if record.stat_name == 'gold_difference_positive':
                        formatted_stat_name = 'GD@15+'
                    elif record.stat_name == 'gold_difference_negative':
                        formatted_stat_name = 'GD@15-'
                    else:
                        formatted_stat_name = " ".join(word.capitalize() for word in record.stat_name.split("_"))
                    summoner = await self.db.get_summoner_by_id(record.summoner_id)
                    field_value = f"**{formatted_stat_name}:** {record.stat_value}\n*Summoner:* {summoner[2]}"
                    embed.add_field(name="\u200B", value=field_value, inline=False)

            await self.channel.send(embed=embed)
        else:
            await ctx.send("Leaderboard is empty.")

    @commands.command()
    async def start(self, ctx, *args):
        self.channel = ctx.channel
        await DiscordMessenger.send_message(message="Bot started. Channel set here.", channel=self.channel)
        self.check_game_status.start()

    @tasks.loop(minutes=3)
    async def check_game_status(self):
        rows = await self.db.get_all_summoners()
        if isinstance(rows, list) and all([isinstance(row, tuple) for row in rows]):
            stalked_summoners_info = [StalkedSummonerInfo(*row) for row in rows]
        else:
            stalked_summoners_info = rows
        for stalked_summoner_info in stalked_summoners_info:
            game = await self.riot.get_current_game(stalked_summoner_info.puuid)
            if game:
                if not stalked_summoner_info.was_in_game:
                    await self.db.set_was_in_game(stalked_summoner_info.puuid, True)
                if stalked_summoner_info.game_id is None:
                    await self.db.set_game_id(stalked_summoner_info.puuid, game['gameId'])
            elif stalked_summoner_info.was_in_game:
                if stalked_summoner_info.game_id is not None:
                    await self.db.set_was_in_game(stalked_summoner_info.puuid, False)
                    game_handler = GameHandler(self.bot)
                    await game_handler.handle_game_result(stalked_summoner_info=stalked_summoner_info,
                                                          channel=self.channel)


async def setup(self):
    await self.add_cog(Stalker(self))
