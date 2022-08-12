import logging

import discord
from discord.ext import commands

from . import button_model
from . import config
from . import meme_model

activity = discord.Activity(type=discord.ActivityType.watching, name="#eth-memes")
bot = commands.Bot(command_prefix="|", activity=activity)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.DATA_PATH + "debug.log"),
        logging.StreamHandler(),
    ],
)

extensions = ["scrape", "memeinfo", "button"]


@bot.event
async def on_ready():
    logging.info("Logged in as {0.user}".format(bot))
    await reload_extensions()
    meme_model.connect()
    button_model.connect()


async def close():
    meme_model.disconnect()
    button_model.disconnect()


@bot.command()
@commands.is_owner()
async def reload(ctx):
    await reload_extensions()


async def reload_extensions():
    for extension in extensions:
        try:
            bot.reload_extension("artarindo.cogs." + extension)
            logging.info(f"Reloaded extension: {extension}")
        except commands.ExtensionNotLoaded:
            bot.load_extension("artarindo.cogs." + extension)
            logging.info(f"Extension {extension} was not loaded, loading now...")


def start():
    bot.run(config.TOKEN)
