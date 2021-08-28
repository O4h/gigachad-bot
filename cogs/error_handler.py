import asyncio
import os
import traceback
import sys
import discord
from discord.ext import commands
from util.misc import get_emote, create_embed
from util.misc import translate as _


class ErrorHandler(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            embed = create_embed(
                title=_("errors.forbidden_cmd.title", ctx),
                color="red",
                desc=_("errors.forbidden_cmd.desc", ctx),
                thumbnail="https://cdn.discordapp.com/emojis/847029255048658975.png?size=32"
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = create_embed(
                color="red",
                title=_("errors.not_in_dms.title", ctx),
                desc=_("errors.not_in_dms.desc", ctx),
                thumbnail="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.MissingPermissions):
            missingperms = ""
            for x in range(len(error.missing_perms)):
                missingperms += f"`{error.missing_perms[x]}` "
            missingperms = missingperms.upper()
            embed = create_embed(
                color="red",
                title=_("errors.missing_perms.title", ctx),
                desc=_("errors.missing_perms.desc", ctx, emote=get_emote("role"), missingperms=missingperms),
                thumbnail="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.BotMissingPermissions):
            missingperms = ""
            for x in range(len(error.missing_perms)):
                missingperms += f"`{error.missing_perms[x]}` "
            missingperms = missingperms.upper()
            embed = create_embed(
                color="red",
                title=_("errors.bot_missing_perms.title", ctx),
                desc=_("errors.bot_missing_perms.desc", ctx, emote=get_emote("role"), missingperms=missingperms),
                thumbnail="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.BadArgument):
            embed = create_embed(
                color="red",
                title=_("errors.bad_argument.title", ctx),
                desc=_("errors.bad_argument.desc", ctx, cmd_name=ctx.command.name,
                       cmd_usage=ctx.command.usage),
                thumnail="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                content=_("errors.cooldown", ctx, emote=get_emote("warning"), time_left=round(error.retry_after)),
                mention_author=False,
                delete_after=error.retry_after
            )

        elif isinstance(error, commands.CommandNotFound):
            pass

        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            channel = await self.gigachad.fetch_channel(os.getenv("LOG_CHANNEL"))
            await channel.send(
                content="```\n {e} \n```".format(e=traceback.format_exception(type(error), error, error.__traceback__))
            )


def setup(gigachad):
    gigachad.add_cog(ErrorHandler(gigachad))
