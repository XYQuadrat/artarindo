from datetime import datetime
from discord.ext import tasks, commands
import discord
from artarindo.button_model import Challenge
from peewee import fn, SQL
import logging

from artarindo.config import CODE


class Button(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.current_code = CODE
        self.active_challenge = None
        self.get_active_challenge()

    def get_active_challenge(self):
        try:
            newest_challenge: Challenge = (
                Challenge.select()
                .where(Challenge.solved_date is None)
                .order_by(Challenge.created_date.desc())
                .get()
            )

            self.active_challenge = newest_challenge
        except Exception:
            self.active_challenge = None

    @commands.group()
    async def button(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                "You probably want to do |button press <code>.", delete_after=10
            )

    @commands.cooldown(3, 24 * 60 * 60, commands.BucketType.user)
    @button.command()
    async def press(self, ctx: commands.Context, code: int):
        if self.active_challenge:
            if code < 1000 or code > 9999:
                await ctx.reply(
                    "Invalid code. The code is a four-digit integer (between 1000 and 9999).",
                    delete_after=10,
                )
                return

            if code == self.current_code:
                points = (
                    datetime.now() - self.active_challenge.created_date
                ).total_seconds() // 3600 + 50

                await ctx.send(
                    "<@&978664537312071750> "
                    + str(ctx.author)
                    + " pressed The Button and claimed "
                    + str(points)
                    + " points!\n"
                    + "If you want to, send a picture of where The Button was hidden and explain how you arrived at the solution."
                )
                ctx.command.reset_cooldown(ctx)
                self.active_challenge.solved_date = datetime.now()
                self.active_challenge.solver = str(ctx.author)
                self.active_challenge.points = points
                self.active_challenge.save()

                self.active_challenge = None
                await self.bot.change_presence(status=discord.Status.idle)
            else:
                await ctx.reply(
                    "That's not the correct code. Are you sure you didn't enter your bank PIN?",
                    delete_after=10,
                )
        else:
            await ctx.reply(
                "The button is currently inactive. You cannot press it.",
                delete_after=10,
            )

    @press.error
    async def press_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                "Slow down, _tyalindo_. You can only make 3 guesses within 24 hours.",
                delete_after=10,
            )

    @button.command()
    @commands.is_owner()
    async def add(self, ctx: commands.Context, challenge_name: str):
        if self.active_challenge:
            await ctx.reply("A challenge is already active.")
        else:
            self.active_challenge = Challenge(name=challenge_name)
            self.active_challenge.save()
            await ctx.reply(
                "Challenge with name "
                + challenge_name
                + " created. Announce the challenge yourself."
            )

            await self.bot.change_presence(status=discord.Status.online)

    @button.command()
    async def leaderboard(self, ctx: commands.Context):
        embed = discord.Embed(title="The Physical Button Game - Leaderboard")
        ranks = ""
        users = ""
        scores = ""

        for i, user in enumerate(
            Challenge.select(
                Challenge.solver,
                fn.SUM(Challenge.points).alias("score"),
                fn.COUNT(Challenge.solved_date).alias("count_solved"),
            )
            .group_by(fn.IFNULL(Challenge.solver, Challenge.created_date))
            .order_by(SQL("score").desc())
            .limit(5)
        ):
            ranks += f"**{i+1}.**\n"
            users += user.solver + "\n"
            scores += str(user.score) + "\n"

        embed.add_field(name="**Rank:**", value=ranks)
        embed.add_field(name="**Player:**", value=users)
        embed.add_field(name="**Score:**", value=scores)
        await ctx.reply(embed=embed)

    @tasks.loop(hours=1.0)
    async def remind(self):
        if self.active_challenge:
            spam = self.bot.get_channel(768600365602963496)
            minutes_active = (
                datetime.now() - self.active_challenge.created_date
            ).total_seconds() // 60

            embed = discord.Embed(
                title="The Button",
                description=f"The Button has been active for **{minutes_active}** minutes and is worth {minutes_active // 60 + 50} points.",
            )

            await spam.send(embed=embed, delete_after=(60 * 60))
            logging.info("Sent reminder to #spam")


def setup(bot):
    bot.add_cog(Button(bot))
