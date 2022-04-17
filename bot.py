import discord
import os
from discord.ext import commands
import config
import sql
import logging

from typing import Optional

bot = commands.Bot(command_prefix="|")
sql_con = sql.connect()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("data/debug.log"), logging.StreamHandler()],
)

UPVOTE_ID = 747783377662378004
DOWNVOTE_ID = 758262252699779073


@bot.event
async def on_ready():
    logging.info("Logged in as {0.user}".format(bot))


def get_score(message):
    upvoteReaction = next(
        (react for react in message.reactions if hash(react) == UPVOTE_ID), None
    )
    downvoteReaction = next(
        (react for react in message.reactions if hash(react) == DOWNVOTE_ID), None
    )

    score = None

    if upvoteReaction is not None and downvoteReaction is not None:
        score = upvoteReaction.count - downvoteReaction.count
    return score


@bot.command()
@commands.is_owner()
async def scrape(
    ctx, channel_id: Optional[int] = None, msg_limit: Optional[int] = None
):
    if channel_id == None:
        channel = ctx.channel
    else:
        channel = bot.get_channel(channel_id)

    logging.info(
        "Getting messages from channel %s with limit = %s", channel.name, msg_limit
    )

    async for message in channel.history(limit=msg_limit):
        for attachment in message.attachments:
            orig_name, extension = os.path.splitext(attachment.filename)
            filename = str(attachment.id) + extension
            logging.info("Processing attachment %s...", filename)

            if sql.exists_record(sql_con, filename):
                logging.info("Attachment %s already exists in DB, skipping", filename)
                continue

            save_path = os.path.join(config.download_path, filename)

            await attachment.save(save_path)

            score = get_score(message)

            sql.insert_meme(
                sql_con,
                filename,
                score,
                message.author.name + "#" + message.author.discriminator,
            )

            logging.info(
                "Inserted attachment %s into DB with score %s", filename, score
            )


@scrape.error
async def scrape_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Only the _oamo_ may use this command.")


bot.run(config.token)
