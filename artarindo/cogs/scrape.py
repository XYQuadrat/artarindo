import logging
import os
from typing import Optional

import discord
import pyvips
from artarindo import config
from discord.ext import commands, tasks

from . import sql

UPVOTE_ID = 747783377662378004
DOWNVOTE_ID = 758262252699779073
IGNORE_ID = 769279807916998728


class Scrape(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        if not self.scrape_new_memes.is_running():
            self.scrape_new_memes.start()

        if not self.scrape_score_updates.is_running():
            self.scrape_score_updates.start()

    def get_score(self, message):
        upvote = next(
            (r for r in message.reactions if str(r) == f"<:this:{UPVOTE_ID}>"), None
        )
        downvote = next(
            (r for r in message.reactions if str(r) == f"<:that:{DOWNVOTE_ID}>"),
            None,
        )

        score = (upvote.count if upvote else 0) - (downvote.count if downvote else 0)

        return score

    def generate_thumbnail(self, read_path: str, write_path: str) -> None:
        if os.path.isfile(write_path):
            return

        out = pyvips.Image.thumbnail(read_path, 256)
        out.write_to_file(write_path)
        logging.info("Created thumbnail at " + write_path)

    @commands.command()
    @commands.is_owner()
    async def scrape(
        self, ctx, channel_id: Optional[int] = None, msg_limit: Optional[int] = None
    ):
        """(Admin-only) Scrape a channel (primarily #eth-memes) for images and videos.
        Download all media and store them in the DB, together with the associated score."""

        if channel_id is None:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(channel_id)

        await self.scrape_channel(msg_limit, channel)

        await ctx.send(
            f"Added {self.newly_added_count} memes to the DB and updated the score for {self.updated_count} memes."
        )

    async def scrape_channel(self, msg_limit, channel):
        logging.info(
            "Getting messages from channel %s with limit = %s", channel.name, msg_limit
        )
        self.newly_added_count = 0
        self.updated_count = 0

        message: discord.Message
        async for message in channel.history(limit=msg_limit):
            # ignore messages with xmark reaction
            if any(str(r) == f"<:xmark:{IGNORE_ID}>" for r in message.reactions):
                logging.info(f"Skipping message with ID {message.id}")
                continue

            for attachment in message.attachments:
                orig_name, extension = os.path.splitext(attachment.filename)
                extension = extension.lower()
                filename = str(attachment.id) + extension
                logging.info("Processing attachment %s...", filename)

                score = self.get_score(message)
                save_path = os.path.join(config.DOWNLOAD_PATH, filename)
                thumbnail_path = os.path.join(config.DOWNLOAD_PATH, "thumb", filename)

                if sql.exists_record(filename):
                    logging.info(
                        "Attachment %s already exists in DB, updating score", filename
                    )
                    sql.update_score(filename, score)

                    if extension in [".jpeg", ".jpg", ".png"]:
                        self.generate_thumbnail(save_path, thumbnail_path)

                    self.updated_count += 1
                    continue

                await attachment.save(save_path)

                sql.insert_meme(
                    filename,
                    score,
                    message.author.name + "#" + message.author.discriminator,
                    message.jump_url,
                    message.created_at,
                )
                self.newly_added_count += 1

                logging.info(
                    "Inserted attachment %s into DB with score %s", filename, score
                )

                if extension in ["jpeg", "jpg", "png"]:
                    self.generate_thumbnail(save_path, thumbnail_path)

    @tasks.loop(minutes=10.0)
    async def scrape_new_memes(self):
        logging.info("Starting scrape of the ten latest messages in #eth-memes")
        await self.scrape_channel(10, self.bot.get_channel(758293511514226718))

    @tasks.loop(hours=24.0)
    async def scrape_score_updates(self):
        logging.info("Starting daily scrape of #eth-memes")
        # await self.scrape_channel(None, self.bot.get_channel(758293511514226718))

    @scrape.error
    async def scrape_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Only the _oamo_ may use this command.")


def setup(bot):
    bot.add_cog(Scrape(bot))
