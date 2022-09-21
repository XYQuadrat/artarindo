from datetime import datetime
import typing
from discord.ext import tasks, commands
import discord
from artarindo import config
from artarindo.button_model import Challenge, Score
from peewee import fn, SQL
import logging

from artarindo.config import CODE


class Button(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.current_code = CODE
        self.active_challenge = None
        self.get_active_challenge()
        if not self.remind.is_running():
            self.remind.start()

    def get_active_challenge(self):
        try:
            newest_challenge: Challenge = (
                Challenge.select()
                .where(Challenge.solved_date.is_null())
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
                    + " pressed The Button which was worth "
                    + str(points)
                    + " points ("
                    + str(points * 1.5) 
                    + " points for groups)!\n"
                    + "If you want to, send a picture of where The Button was hidden and explain how you arrived at the solution."
                )
                ctx.command.reset_cooldown(ctx)
                self.active_challenge.solved_date = datetime.now()
                self.active_challenge.solver = str(ctx.author)
                self.active_challenge.points = points
                self.active_challenge.save()
                
                solvers = [member.name for member in ctx.message.mentions]
                solvers.append(ctx.author.name)
                
                if len(solvers) > 1:
                    points *= 1.5
                    # only keep unique names
                    solvers = list(set(solvers))
                    
                points_per_solver = points // len(solvers) 
                await ctx.send(f"All solvers have received {points_per_solver} points.")
                for solver in solvers:
                    score = Score(challenge_id=self.active_challenge.id, username=solver, score=points_per_solver)
                    score.save()

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
            self.active_challenge = Challenge(name=challenge_name, season=config.BUTTON_SEASON)
            self.active_challenge.save()
            await ctx.reply(
                "Challenge with name "
                + challenge_name
                + " created. Announce the challenge yourself."
            )

            await self.bot.change_presence(status=discord.Status.online)

    @button.command()
    async def leaderboard(self, ctx: commands.Context, season: typing.Optional[int] = config.BUTTON_SEASON):
        embed = discord.Embed(title=f"The Button Game - Season {season} Leaderboard")
        ranks = ""
        users = ""
        scores = ""

        for i, user in enumerate(
            Challenge.select(
                Challenge.solver,
                fn.SUM(Challenge.points).alias("score"),
                fn.COUNT(Challenge.solved_date).alias("count_solved"),
            )
            .where((Challenge.season == season) & (Challenge.solver.is_null(False)))
            .group_by(Challenge.solver)
            .order_by(SQL("score").desc())
            .limit(5)
        ):
            ranks += f"**{i+1}.**\n"
            users += user.solver + "\n"
            scores += str(user.score) + "\n"

        if ranks == "":
            await ctx.reply("No scores recorded for this season yet.")
        else:
            embed.add_field(name="**Rank:**", value=ranks)
            embed.add_field(name="**Player:**", value=users)
            embed.add_field(name="**Score:**", value=scores)
            await ctx.reply(embed=embed)

    @tasks.loop(hours=6.0)
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


async def setup(bot):
    await bot.add_cog(Button(bot))
