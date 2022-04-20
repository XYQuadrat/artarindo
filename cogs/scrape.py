import discord
from discord.ext import commands

import logging
import cogs.sql as sql
from typing import Optional
import os
import config


UPVOTE_HASH = 178285450378
DOWNVOTE_HASH = 180783808875


class Scrape(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.sql_con = sql.connect()

    def get_score(self, message):
        upvoteReaction = next(
            (r for r in message.reactions if hash(r) == UPVOTE_HASH), None
        )
        downvoteReaction = next(
            (r for r in message.reactions if hash(r) == DOWNVOTE_HASH), None
        )

        score = None

        if upvoteReaction is not None and downvoteReaction is not None:
            score = upvoteReaction.count - downvoteReaction.count
        return score

    @commands.command()
    @commands.is_owner()
    async def scrape(
        self, ctx, channel_id: Optional[int] = None, msg_limit: Optional[int] = None
    ):
        """(Admin-only) Scrape a channel (primarily #eth-memes) for images and videos. Download all media and store them in the DB, together with the associated score."""
        newly_added_count = 0
        updated_count = 0

        if channel_id == None:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(channel_id)

        logging.info(
            "Getting messages from channel %s with limit = %s", channel.name, msg_limit
        )

        async for message in channel.history(limit=msg_limit):
            for attachment in message.attachments:
                orig_name, extension = os.path.splitext(attachment.filename)
                filename = str(attachment.id) + extension
                logging.info("Processing attachment %s...", filename)

                score = self.get_score(message)

                if sql.exists_record(self.sql_con, filename):
                    logging.info(
                        "Attachment %s already exists in DB, updating score", filename
                    )
                    sql.update_score(self.sql_con, filename, score)
                    updated_count += 1
                    continue

                save_path = os.path.join(config.download_path, filename)

                await attachment.save(save_path)

                sql.insert_meme(
                    self.sql_con,
                    filename,
                    score,
                    message.author.name + "#" + message.author.discriminator,
                )
                newly_added_count += 1

                logging.info(
                    "Inserted attachment %s into DB with score %s", filename, score
                )

        await ctx.send(
            f"Added {newly_added_count} memes to the DB and updated the score for {updated_count} memes."
        )

    @scrape.error
    async def scrape_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Only the _oamo_ may use this command.")


def setup(bot):
    bot.add_cog(Scrape(bot))
