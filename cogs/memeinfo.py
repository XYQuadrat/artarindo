from typing import Optional
import discord
from discord.ext import commands

import cogs.sql as sql


class Memeinfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.sql_con = sql.connect()

    @commands.command()
    async def memeinfo(
        self, ctx: commands.Context, user: Optional[discord.User] = None
    ):
        """Get statistics about your meme game in #eth-memes.
        Optionally takes a mention of a user as an argument to look up their stats."""
        if user:
            username = user.name + "#" + user.discriminator
        else:
            username = ctx.author.name + "#" + ctx.author.discriminator

        if not sql.user_has_records(self.sql_con, username):
            await ctx.send(
                "No memes from #eth-memes are associated with your username."
            )
        else:
            info = UserInfo()
            sql.user_get_score_info(self.sql_con, username, info)
            sql.user_get_count_info(self.sql_con, username, info)
            sql.user_get_hindex(self.sql_con, username, info)

            msg = discord.Embed(
                description=f"Meme Statistics For {username}",
                color=discord.Color.dark_blue(),
            )
            msg.add_field(
                name="No. of Memes",
                value=f"You have sent `{info.count}` meme{'s'[:info.count^1]} in #eth-memes, which places you on rank `{info.count_rank}`.",
            )
            msg.add_field(
                name="Average Karma",
                value=f"The average karma score of your meme{'s'[:info.count^1]} is `{info.score_avg:.2f}`, which places you on rank `{info.score_rank}`.",
            )
            msg.add_field(
                name="h-index",
                value=f"You have a h-index of `{info.hindex}` (that means {info.hindex} meme{'s'[:info.hindex^1]} with at least {info.hindex} karma).",
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
    hindex = 0
