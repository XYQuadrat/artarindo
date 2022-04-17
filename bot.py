import discord
import os
from discord.ext import commands
import config
import sql
import logging

bot = commands.Bot(command_prefix="|")
sql_con = sql.connect()
logging.basicConfig(level=logging.INFO)

UPVOTE_ID = 747783377662378004
DOWNVOTE_ID = 758262252699779073


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def scrape(ctx):
    async for message in ctx.channel.history(limit=None):
        for attachment in message.attachments:
            orig_name, extension = os.path.splitext(attachment.filename)
            filename = str(attachment.id) + extension
            logging.info("Processing attachment %s...", filename)

            if sql.exists_record(sql_con, filename):
                logging.info("Attachment %s already exists in DB, skipping", filename)
                continue

            save_path = os.path.join(config.download_path, filename)

            await attachment.save(save_path)

            upvoteReaction = next(
                (r for r in message.reactions if hash(r) == UPVOTE_ID), None
            )
            downvoteReaction = next(
                (r for r in message.reactions if hash(r) == DOWNVOTE_ID), None
            )

            upvotes = None
            downvotes = None
            score = None

            if upvoteReaction is not None and downvoteReaction is not None:
                upvotes = upvoteReaction.count
                downvote = downvoteReaction.count
                score = upvotes - downvote

            sql.insert_meme(
                sql_con,
                filename,
                score,
                message.author.name + "#" + message.author.discriminator,
            )

            logging.info("Inserted attachment %s into DB", filename)


bot.run(config.token)
