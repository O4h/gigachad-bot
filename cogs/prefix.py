import discord
import asyncio
import json
from discord.ext import commands


def get_prefix(bot, message, raw=False):
    if message.guild is not None:
        with open('prefixes.json', 'r') as f:
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

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix=None):
        if prefix is None:
            current_prefix = get_prefix(self, ctx, True)
            embed = discord.Embed(color=0x2f3136, title="Current Prefix",
                                  description=f"My current prefix is `{current_prefix}`. \n Execute `{current_prefix}pre"
                                              "fix newprefix` to set a new prefix!")

        else:
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)

            prefixes[str(ctx.guild.id)] = prefix

            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)

            embed = discord.Embed(color=0x57f287, title="Prefix succesfully changed",
                                  description=f"My prefix for this server has succefully been changed to `{prefix}`.")

        await ctx.send(embed=embed)


def setup(gigachad):
    gigachad.add_cog(Prefix(gigachad))
