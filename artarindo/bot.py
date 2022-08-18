import logging

import discord
from discord.ext import commands

from . import button_model
from . import config
from . import meme_model

activity = discord.Activity(type=discord.ActivityType.watching, name="#eth-memes")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="|", activity=activity, intents=intents)
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
    await load_extensions()
    meme_model.connect()
    button_model.connect()


async def close():
    meme_model.disconnect()
    button_model.disconnect()


async def load_extensions():
    for extension in extensions:
        await bot.load_extension("artarindo.cogs." + extension)
        logging.info(f"Extension {extension} was not loaded, loading now...")


def start():
    bot.run(config.TOKEN)
