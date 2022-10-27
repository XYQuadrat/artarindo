from typing import Optional
from unicodedata import name
import discord
from discord.ext import commands

from . import sql
from . import user_info


class Memeinfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def memeinfo(
        self, ctx: commands.Context, user: Optional[discord.Member] = None
    ):
        """Get statistics about your meme game in #eth-memes.
        Optionally takes a mention of a user as an argument to look up their stats."""
        if not user:
            user = ctx.author

        if not sql.user_has_records(user.id):
            await ctx.send(
                "No memes from #eth-memes are associated with your username."
            )
        else:
            info = user_info.UserInfo()
            sql.user_get_score_info(user.id, info)
            sql.user_get_count_info(user.id, info)
            sql.user_get_hindex(user.id, info)

            username = user.nick if user.nick else user.name
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


async def setup(bot):
    await bot.add_cog(Memeinfo(bot))
