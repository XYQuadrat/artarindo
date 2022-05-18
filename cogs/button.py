from datetime import date
from tabnanny import check
from discord.ext import commands
import discord
from button_model import *
import typing

from config import CODE


class Button(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.current_code = CODE
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

                ctx.send(
                    ctx.author
                    + " pressed the button and claimed "
                    + points
                    + " points!"
                )
                commands.Cooldown.reset()
                self.challenge_active = False
            else:
                ctx.reply(
                    "That's not the correct code. Are you sure you didn't enter your bank PIN?"
                )
        else:
            ctx.reply("The button is currently inactive. You cannot press it.")

    @press.error()
    async def press_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.reply(
                "Slow down, _tyalindo_. You can only make 3 guesses within 24 hours."
            )

    @button.command()
    @commands.is_owner()
    async def add(self, ctx: commands.Context, challenge_name: str):
        challenge = Challenge(name=challenge_name)
        challenge.save()
        ctx.reply(
            "Challenge with name "
            + challenge_name
            + "created. For now, you must announce the challenge yourself."
        )
        self.challenge_active = True
        self.challenge_start_time = datetime.now()


def setup(bot):
    bot.add_cog(Button(bot))
