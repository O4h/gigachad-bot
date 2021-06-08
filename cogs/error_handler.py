import discord
import asyncio
import traceback

from discord.ext import commands
from util.emotes import get_emote


class Errors(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="Forbidden Command",
                color=0xed4245,
                description="Only the bot owner can execute this command"
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/847029255048658975.png?size=32"
            )
            await ctx.reply(
                embed=embed,
                mention_author=False
            )

        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                color=0xed4245,
                title="Not in DMs",
                description="This commands **can not** be executed in direct messages, only in "
                            "servers!"
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(
                embed=embed,
                mention_author=False
            )

        elif isinstance(error, commands.MissingPermissions):
            missingperms = ""
            for x in range(len(error.missing_perms)):
                missingperms += f"`{error.missing_perms[x]}` "
            missingperms = missingperms.upper()
            embed = discord.Embed(
                color=0xed4245,
                title="Missing Permissions",
                description=f"{get_emote(role)} You are missing the permission(s) "
                            f"{missingperms}"
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(
                embed=embed,
                mention_author=False
            )

        elif isinstance(error, commands.BotMissingPermissions):
            missingperms = ""
            for x in range(len(error.missing_perms)):
                missingperms += f"`{error.missing_perms[x]}` "
            missingperms = missingperms.upper()
            embed = discord.Embed(
                color=0xed4245,
                title="Bot Missing Permissions",
                description=f"{get_emote(role)} I am missing the following permission(s):" + missingperms
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(
                embed=embed,
                mention_author=False
            )

        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                                  color=0xed4245,
                                  title="Wrong Argument(s)",
                                  description=f" You entered wrong arguments for the `{ctx.command.name}` command. \n"
                                              f"Use it like that: `{ctx.command.usage}`"
                                  )
            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
                                )
            await ctx.reply(
                            embed=embed,
                            mention_author=False
                            )

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                            content=f"{get_emote(warning)} Please wait `{round(error.retry_after)}` "
                                    f"seconds before using this command again!",
                            mention_author=False,
                            delete_after=error.retry_after
                            )

        else:
            traceback.print_exception(type(error), error, error.__traceback__)


def setup(gigachad):
    gigachad.add_cog(Errors(gigachad))
