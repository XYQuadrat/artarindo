from cmath import inf
from operator import truediv
import discord
from discord.ext import commands

import cogs.sql as sql


class Memeinfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.sql_con = sql.connect()

    @commands.command()
    async def memeinfo(self, ctx: commands.Context):
        username = ctx.author.name + "#" + ctx.author.discriminator
        if not sql.user_has_records(self.sql_con, username):
            ctx.send("No memes from #eth-memes are associated with your username.")
        else:
            info = UserInfo()
            sql.user_get_score_info(self.sql_con, username, info)
            sql.user_get_count_info(self.sql_con, username, info)

            msg = discord.Embed(description=f"Memeinfo for {username}")
            msg.add_field(
                name="No. of Memes",
                value=f"You have sent `{info.count}` memes in #eth-memes, which places you on rank `{info.count_rank}`.",
            )
            msg.add_field(
                name="Average Karma",
                value=f"Your memes have an average karma score of `{info.score_avg}`, which places you on rank `{info.score_rank}`.",
            )

            await ctx.reply(embed=msg)


def setup(bot):
    bot.add_cog(Memeinfo(bot))


class UserInfo:
    def __init__(self) -> None:
        pass

    score_avg = 0
    score_rank = 0
    count = 0
    count_rank = 0
