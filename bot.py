import logging

import discord
from discord.ext import commands

import config

activity = discord.Activity(type=discord.ActivityType.watching, name="#eth-memes")
bot = commands.Bot(command_prefix="|", activity=activity)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("data/debug.log"), logging.StreamHandler()],
)

extensions = ["scrape", "memeinfo", "button"]


@bot.event
async def on_ready():
    logging.info("Logged in as {0.user}".format(bot))
    await reload_extensions()


@bot.command()
@commands.is_owner()
async def reload(ctx):
    await reload_extensions()


async def reload_extensions():
    for extension in extensions:
        try:
            bot.reload_extension("cogs." + extension)
            logging.info(f"Reloaded extension: {extension}")
        except Exception as e:
            bot.load_extension("cogs." + extension)
            logging.info(f"Extension {extension} was not loaded, loading now...")


bot.run(config.TOKEN)
