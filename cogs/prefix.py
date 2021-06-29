import discord
import asyncio
import json
from discord.ext import commands


def get_prefix(bot, message, raw: bool = False):
    if message.guild is not None:
        with open('/data/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        if str(message.guild.id) in prefixes:
            if raw:
                return prefixes[str(message.guild.id)]
            else:
                return commands.when_mentioned_or(prefixes[str(message.guild.id)])(bot, message)

        else:
            if raw:
                return "gc!"
            else:
                return commands.when_mentioned_or("gc!")(bot, message)

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
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        if str(guild.id) in prefixes:
            prefixes.pop(str(guild.id))

            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)


def setup(gigachad):
    gigachad.add_cog(Prefix(gigachad))
