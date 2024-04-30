import discord
from discord.ext import commands

from config import discord_bot_token

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


async def setup_cogs():
    initial_extensions = ['Stalker']
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await setup_cogs()


bot.run(discord_bot_token)
