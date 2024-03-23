import discord
from discord.ext import commands, tasks
import riot_api as Riot
import database as DB

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

channel = None


@client.event
async def on_ready():
    DB.initialize_database()
    check_game_status.start()

@client.event
async def on_disconnect():
    DB.close_connection()
    
# Commands
@client.command()
async def stalk(ctx, *args):
    global channel
    channel = ctx.channel

    for arg in args:
        if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
            await send_message("Invalid summoner name, must be in this format (no spaces): example#na1")
            return
        game_name, tag_line = arg.split("#")

        summoner_puuid = DB.get_summoner_puuid(game_name, tag_line)
        if summoner_puuid:
            await send_embed(
                title="Sitting in a bush",
                description=f"Now stalking {game_name}",
                color=discord.Color.dark_embed())
        else:
            summoner_data = Riot.get_summoner_puuid(game_name, tag_line)
            if summoner_data:
                puuid = summoner_data['puuid']
                gameName = summoner_data['gameName']
                tagLine = summoner_data['tagLine']
                DB.insert_summoner(puuid, gameName, tagLine)
                await send_embed(
                    title="Sitting in a bush",
                    description=f"Now stalking {gameName}#{tagLine}",
                    color=discord.Color.dark_embed())
            else:
                await send_message(f"Failed to find summoner with name {game_name}#{tag_line}")


@client.command()
async def unstalk(ctx, *args):
    global channel
    channel = ctx.channel

    for arg in args:
        if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
            await send_message(f"Invalid summoner name, must be in this format (no spaces): example#na1")
            return
        game_name, tag_line = arg.split("#")

        summoner_puuid = DB.get_summoner_puuid(game_name, tag_line)
        if summoner_puuid:
            DB.delete_summoner(summoner_puuid)
            await send_message(f"Stopped stalking {game_name}#{tag_line}")
        else:
            await send_message(f"You're not currently stalking {game_name}#{tag_line}")


@tasks.loop(minutes=3)
async def check_game_status():
    all_tracked_summoners = DB.get_all_summoners()
    for summoner_puuid, game_name, tag_line, gameId, was_in_game, consecutive_losses, consecutive_wins, time_wasted in all_tracked_summoners:
        game = Riot.get_current_game(summoner_puuid)
        if game['in_game']:
            if not was_in_game:
                DB.set_was_in_game(summoner_puuid, True)
            if gameId == None:
                DB.set_game_id(summoner_puuid, game['gameId'])
        elif was_in_game:
            if gameId != None:
                DB.set_was_in_game(summoner_puuid, False)
                await handle_game_result(summoner_puuid, game_name, gameId)


async def handle_game_result(summoner_puuid, game_name, gameId):
    game_won, game_duration = Riot.check_last_game(gameId, summoner_puuid)
    game_duration_minutes = game_duration // 60

    if game_won:
       await handle_win(summoner_puuid, game_name, game_duration_minutes)
    else:
       await handle_loss(summoner_puuid, game_name, game_duration_minutes)
    DB.set_game_id(summoner_puuid, None)


async def handle_win(summoner_puuid, game_name, game_duration_minutes):
    await send_embed(
        title="VICTORY",
        description=f"{summoner_name} won a game in {game_duration_minutes}!!",
        color=discord.Color.green()
    )

    DB.set_consecutive_losses(summoner_puuid, 0)
    consecutive_wins += 1
    DB.set_consecutive_wins(summoner_puuid, consecutive_wins)

    if consecutive_wins >= 3:
        await send_embed(
            title="Win streak!",
            description=f"{game_name} has won {consecutive_wins} games in a row!",
            color=discord.Color.blue()
        )


async def handle_loss(summoner_puuid, game_name, game_duration_minutes):
    await send_embed(
        title="DEFEAT",
        description=f"{summoner_name} wasted {game_duration_minutes} minutes on a game just to lose",
        color=discord.Color.red())
    DB.set_consecutive_wins(summoner_puuid, 0)
    time_wasted += game_duration_minutes
    consecutive_losses += 1
    DB.set_consecutive_losses(summoner_puuid, consecutive_losses)
    DB.set_time_wasted(summoner_puuid, time_wasted)

    if consecutive_losses >= 3:
        await send_embed(
            title="Lose streak!",
            description=f"{game_name} has lost {consecutive_losses} games in a row for a grand total of {time_wasted} minutes!",
            color=discord.Color.brand_red()
        )
        # Reset consecutive losses counter
        DB.set_consecutive_losses(summoner_puuid, 0)


# Message sending
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
