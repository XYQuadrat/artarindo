from datetime import datetime
from discord.ext import commands
import discord
from button_model import *
import typing

from config import CODE


class Button(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.current_code = CODE
        self.active_challenge = None
        self.get_active_challenge()

        self.challenge_start_time = datetime.now()

    def get_active_challenge(self):
        try:
            newest_challenge: Challenge = (
                Challenge.select()
                .where(Challenge.solved_date == None)
                .order_by(Challenge.created_date.desc())
                .get()
            )

            self.active_challenge = newest_challenge
        except:
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
                    datetime.now() - self.challenge_start_time
                ).total_seconds() // 3600 + 50

                await ctx.send(
                    str(ctx.author)
                    + " pressed the button and claimed "
                    + str(points)
                    + " points!"
                )
                ctx.command.reset_cooldown(ctx)
                self.active_challenge.solved_date = datetime.now()
                self.active_challenge.solver = str(ctx.author)
                self.active_challenge.points = points
                self.active_challenge.save()

                self.active_challenge = None
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
                + " created. For now, you must announce the challenge yourself."
            )
            self.challenge_start_time = datetime.now()

    @button.command()
    async def leaderboard(self, ctx: commands.Context):
        embed = discord.Embed(title="The Physical Button Game - Leaderboard")
        for user in (
            Challenge.select(Challenge.solver, fn.SUM(Challenge.points).alias("score"))
            .group_by(Challenge.solver)
            .limit(10)
        ):
            embed.add_field(name=user.solver, value=user.score)

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Button(bot))
