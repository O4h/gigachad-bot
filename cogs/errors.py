import discord
import asyncio
import traceback
from discord.ext import commands


class Errors(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(title="Forbidden Command",
                                  color=0xed4245, description="Only the bot owner can execute this command")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/847029255048658975.png?size=32")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(color=0xed4245, title="Not in DMs",
                                  description="This commands **can not** be executed in direct messages, only in "
                                              "servers!")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            missingperms = ""
            for x in range(len(error.missing_perms)):
                missingperms += f"`{error.missing_perms[x]}` "
            missingperms = missingperms.upper()
            embed = discord.Embed(color=0xed4245, title="Missing Permissions",
                                  description=f" <:gc_role:847078576058138644> You are missing the permission(s) "
                                              f"{missingperms}")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            missingperms = ""
            for x in range(len(error.missing_perms)):
                missingperms += f"`{error.missing_perms[x]}` "
            missingperms = missingperms.upper()
            embed = discord.Embed(color=0xed4245, title="Bot Missing Permissions",
                                  description=f" <:gc_role:847078576058138644> I am missing the following permission(s):"
                                              f" {missingperms}")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32")
            await ctx.send(embed=embed)

        else:
            traceback.print_exception(type(error), error, error.__traceback__)


def setup(gigachad):
    gigachad.add_cog(Errors(gigachad))
