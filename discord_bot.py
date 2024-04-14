import discord
from discord.ext import commands, tasks
import riot_api as Riot
import database as DB
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

channel = None


@client.event
async def on_ready():
    DB.initialize_database()


# Commands
@client.command()
async def stalk(ctx, *args):
    for arg in args:
        if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
            await send_message("Invalid summoner name, must be in this format (no spaces): example#na1")
            return
        game_name, tag_line = arg.split("#")

        db_summoner_data = DB.get_summoner(game_name, tag_line)
        if db_summoner_data:
            db_game_name, db_tag_line, db_summoner_puuid = db_summoner_data
            await send_embed(
                title="Sitting in a bush",
                description=f"Now stalking {db_game_name}#{db_tag_line}",
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
    for arg in args:
        if "#" not in arg or arg.index("#") == 0 or arg.index("#") == len(arg) - 1:
            await send_message(f"Invalid summoner name, must be in this format (no spaces): example#na1")
            return
        game_name, tag_line = arg.split("#")

        db_summoner_data = DB.get_summoner(game_name, tag_line)
        if db_summoner_data:
            db_game_name, db_tag_line, db_summoner_puuid = db_summoner_data
            DB.delete_summoner(db_summoner_puuid)
            await send_embed(
                title="Out of the bush",
                description=f"Stopped stalking {db_game_name}#{db_tag_line}",
                color=discord.Color.dark_embed())
        else:
            await send_embed(
                title="Who?",
                description=f"You're not currently stalking {game_name}#{tag_line}",
                color=discord.Color.dark_embed())


@client.command()
async def stalklist(ctx):
    stalked_players = DB.get_all_summoners()

    if stalked_players:
        embed_title = "Stalk List"
        embed_description = ""
        embed_color = discord.Color.green()

        for player in stalked_players:
            puuid, game_name, tag_line, *_ = player
            embed_description += f"**{game_name}#{tag_line}**\n"

        await send_embed(embed_title, embed_description, embed_color)
    else:
        await send_embed("Stalk List", "No players are currently being stalked.", discord.Color.red())


@client.command()
async def start(ctx, *args):
    global channel
    channel = ctx.channel
    await send_message("Bot started. Channel set here.")
    check_game_status.start()


@tasks.loop(minutes=3)
async def check_game_status():
    all_tracked_summoners = DB.get_all_summoners()
    for summoner_puuid, game_name, tag_line, gameId, was_in_game, consecutive_losses, consecutive_wins, time_wasted in all_tracked_summoners:
        game = Riot.get_current_game(summoner_puuid)
        if game:
            if game['in_game']:
                if not was_in_game:
                    DB.set_was_in_game(summoner_puuid, True)
                if gameId is None:
                    DB.set_game_id(summoner_puuid, game['gameId'])
            elif was_in_game:
                if gameId is not None:
                    DB.set_was_in_game(summoner_puuid, False)
                    await handle_game_result(summoner_puuid, game_name, gameId, consecutive_losses, consecutive_wins,
                                             time_wasted)


async def handle_game_result(summoner_puuid, game_name, gameId, consecutive_losses, consecutive_wins, time_wasted):
    game_result = Riot.check_last_game(gameId, summoner_puuid)
    if game_result is not None:
        game_won, summoner_data = game_result
        game_duration_minutes = summoner_data['duration'] // 60

        if game_won:
            await handle_win(summoner_puuid, game_name, game_duration_minutes, consecutive_wins, time_wasted,
                             summoner_data)
        else:
            await handle_loss(summoner_puuid, game_name, game_duration_minutes, consecutive_losses, time_wasted,
                              summoner_data)
        DB.set_game_id(summoner_puuid, None)


async def handle_win(summoner_puuid, game_name, game_duration_minutes, consecutive_wins, time_wasted, summoner_data):
    await send_embed(
        title="VICTORY",
        description=f"{game_name} won a game in {game_duration_minutes} minutes!!",
        color=discord.Color.green(),
        summoner_data=summoner_data
    )

    if DB.get_consecutive_losses(summoner_puuid) > 0:
        DB.set_consecutive_losses(summoner_puuid, 0)
        DB.set_time_wasted(summoner_puuid, 0)
        time_wasted = 0
    DB.set_consecutive_losses(summoner_puuid, 0)
    consecutive_wins += 1
    time_wasted += game_duration_minutes
    DB.set_time_wasted(summoner_puuid, time_wasted)
    DB.set_consecutive_wins(summoner_puuid, consecutive_wins)

    if consecutive_wins >= 3:
        await send_embed(
            title="Win streak!",
            description=f"{game_name} has won {consecutive_wins} games in a row!",
            color=discord.Color.blue(),
        )


async def handle_loss(summoner_puuid, game_name, game_duration_minutes, consecutive_losses, time_wasted, summoner_data):
    await send_embed(
        title="DEFEAT",
        description=f"{game_name} wasted {game_duration_minutes} minutes on a game just to lose",
        color=discord.Color.red(),
        summoner_data=summoner_data
    )
    print('loss')
    if DB.get_consecutive_wins(summoner_puuid) > 0:
        print('loss consecutive wins if')

        DB.set_consecutive_wins(summoner_puuid, 0)
        DB.set_time_wasted(summoner_puuid, 0)
        time_wasted = 0
    DB.set_consecutive_wins(summoner_puuid, 0)

    time_wasted += game_duration_minutes
    consecutive_losses += 1
    DB.set_consecutive_losses(summoner_puuid, consecutive_losses)
    DB.set_time_wasted(summoner_puuid, time_wasted)

    if consecutive_losses >= 3:
        await send_embed(
            title="Lose streak!",
            description=f"{game_name} has lost {consecutive_losses} games in a row for a grand total of {time_wasted} minutes!",
            color=discord.Color.brand_red(),
        )


# Message sending
async def send_message(message):
    global channel
    await channel.send(message)


async def send_embed(title, description, color, summoner_data=None):
    global channel
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    if summoner_data:
        embed.add_field(name="Role", value=summoner_data['teamPosition'], inline=True)
        embed.add_field(name="Champion", value=summoner_data['championName'], inline=True)
        embed.add_field(name="Kills", value=str(summoner_data['kills']), inline=True)
        embed.add_field(name="Deaths", value=str(summoner_data['deaths']), inline=True)
        embed.add_field(name="Assists", value=str(summoner_data['assists']), inline=True)
        embed.add_field(name="Gold Earned", value=str(summoner_data['goldEarned']), inline=True)
        embed.add_field(name="Minions Killed", value=str(summoner_data['minionKilled']), inline=True)
        embed.add_field(name="Wards Placed", value=str(summoner_data['wardsPlaced']), inline=True)
        embed.add_field(name="Damage Dealt", value=str(summoner_data['damageDealt']), inline=True)
        embed.add_field(name="Damage Taken", value=str(summoner_data['damageTaken']), inline=True)
        embed.add_field(name="Damage Struct.", value=str(summoner_data['damageBuildings']), inline=True)
        embed.add_field(name="Side", value=str(summoner_data['side']), inline=True)
        embed.add_field(name="GD@15", value=str(summoner_data['goldDifference']), inline=True)

    await channel.send(embed=embed)
