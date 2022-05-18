from datetime import datetime
from tabnanny import check
from discord.ext import commands
import discord
from . import button_model
import typing

from config import CODE


class Button(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.current_code = CODE
        self.challenge = None
        self.challenge_active = False
        self.challenge_start_time = datetime.now()

    @commands.group()
    async def button(self, ctx):
        pass

    @commands.cooldown(3, 24 * 60 * 60, commands.BucketType.user)
    @button.command()
    async def press(self, ctx: commands.Context, code: int):
        if self.challenge_active:
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
                self.challenge
                self.challenge_active = False
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
        if self.challenge_active:
            await ctx.reply("A challenge is already active.")
        else:
            self.challenge = button_model.Challenge(name=challenge_name)
            self.challenge.save()
            await ctx.reply(
                "Challenge with name "
                + challenge_name
                + " created. For now, you must announce the challenge yourself."
            )
            self.challenge_active = True
            self.challenge_start_time = datetime.now()


def setup(bot):
    bot.add_cog(Button(bot))
