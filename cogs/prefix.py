import asyncio
import json
import asyncpg
import discord
from discord.ext import commands


def get_prefix(bot: commands.Bot, message, raw: bool = False) -> str:
    """
    Get the prefix with a given context
    :param message: Can be a msg or a ctx
    :param raw: Whether the prefix should be raw or
    :param bot: Needs to be the gigachad bot instance
    """
    if message.guild is not None and message.guild.id in bot.prefix_cache:

        if raw:
            return bot.prefix_cache[message.guild.id]
        else:
            return commands.when_mentioned_or(bot.prefix_cache[message.guild.id])(bot, message)

    else:
        if raw:
            return "gc!"
        else:
            return commands.when_mentioned_or("gc!")(bot, message)


class Prefix(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """" Remove custom prefixes from the db if guild is left"""
        if guild.id in self.gigachad.prefix_cache:
            self.gigachad.prefix_cache.pop(guild.id)

            async with self.gigachad.db.acquire() as conn:
                await conn.execute("DELETE FROM lang WHERE guild = $1", guild.id)

    @commands.command()
    @commands.is_owner()
    async def test(self, ctx):
        await ctx.send(self.gigachad.prefix_cache)


def setup(gigachad):
    gigachad.add_cog(Prefix(gigachad))
