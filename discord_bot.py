import discord
from discord.ext import commands, tasks
import riot_api as Riot
import asyncio
import config as Config

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

player_tracking_info = {}
channel = None


@client.event
async def on_ready():
    check_game_status.start()


@client.command()
async def stalk(ctx, *args):
    global channel
    channel = ctx.channel

    for arg in args:
        if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
            await send_message(f"Invalid summoner name, must be in this format : example#na1")
            continue

        game_name, tag_line = arg.split("#")
        summoner_data = Riot.get_summoner_puuid(game_name, tag_line)
        if summoner_data:
            player_tracking_info[summoner_data['puuid']] = {"game_name": summoner_data['gameName']}
            await send_embed(f"Sitting in a bush", f"Now stalking {game_name}", discord.Color.dark_embed())
        else:
            await send_message(f"Failed to find summoner with name {game_name}#{tag_line}")


@tasks.loop(minutes=5)
async def check_game_status():
    for summoner_puuid, tracking_info in player_tracking_info.items():
        game = Riot.get_current_game(summoner_puuid)
        summoner_name = tracking_info.get("game_name")
        if game['in_game']:
            if "gameId" not in tracking_info:
                tracking_info["gameId"] = game['gameId']
            tracking_info["was_in_game"] = True

        elif not game['in_game'] and "was_in_game" in tracking_info:
            if "gameId" in tracking_info:
                del tracking_info["was_in_game"]
                # if won
                game_won, game_duration = Riot.check_last_game(tracking_info["gameId"], summoner_puuid)
                game_duration_minutes = game_duration // 60
                if game_won:
                    await send_embed(f"VICTORY", f"{summoner_name} won a game yipee!!", discord.Color.green())
                else:
                    await send_embed(f"DEFEAT",
                                     f"{summoner_name} wasted {game_duration_minutes} minutes on a game just to lose",
                                     discord.Color.red())
                del tracking_info["gameId"]


async def send_message(message):
    global channel
    await channel.send(message)


async def send_embed(title, description, color):
    global channel
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await channel.send(embed=embed)
