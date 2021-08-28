import discord
from discord.ext import commands


def get_lang(bot: commands.Bot, ctx) -> str:
    """ Returns a lang with a given ctx
    :param ctx: can be commands.Context or discord.Message
     """
    if ctx.guild is not None and ctx.guild.id in bot.lang_cache:
        # If it is in a guild basically and if a different language than default is set
        return bot.lang_cache[ctx.guild.id]
    else:
        return "en"  # Return the default language


class Lang(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.command()
    @commands.is_owner()
    async def testa(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Lang(bot))
