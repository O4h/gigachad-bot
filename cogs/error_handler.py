import asyncio
import os
import traceback
import sys
import disnake
from disnake.ext import commands

from util.misc import get_emote, create_embed
from util.misc import translate as _


class ErrorHandler(commands.Cog):
    def __init__(self, gigachad):
        """ Errors are handled here, unknow ones are sent to LOG_CHANNEL  """
        self.gigachad = gigachad

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.NotOwner):
            embed = create_embed(
                title=_("errors.forbidden_cmd.title", ctx),
                color="red",
                desc=_("errors.forbidden_cmd.desc", ctx),
                thumbnail=get_emote('forbidden', return_type='image')
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = create_embed(
                color="red",
                title=_("errors.not_in_dms.title", ctx),
                desc=_("errors.not_in_dms.desc", ctx),
                thumbnail=get_emote('no', return_type='image')
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.MissingPermissions):
            missingperms = "".join(
                f"`{error.missing_perms[x]}` "
                for x in range(len(error.missing_perms))
            )

            missingperms = missingperms.upper()
            embed = create_embed(
                color="red",
                title=_("errors.missing_perms.title", ctx),
                desc=get_emote("role") + _("errors.missing_perms.desc", ctx, missingperms=missingperms),
                thumbnail=get_emote('no', return_type='image')
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.BotMissingPermissions):
            try:
                missingperms = "".join(
                    f"`{error.missing_perms[x]}` "
                    for x in range(len(error.missing_perms))
                )

                missingperms = missingperms.upper()
                embed = create_embed(
                    color="red",
                    title=_("errors.bot_missing_perms.title", ctx),
                    desc=_("errors.bot_missing_perms.desc", ctx, emote=get_emote("role"), missingperms=missingperms),
                    thumbnail=get_emote('no', return_return_type='image')
                )
                await ctx.reply(embed=embed, mention_author=False)

            except disnake.Forbidden or disnake.HTTPException:  # Bot can't send messages, not much we can do about it :/
                pass

        elif isinstance(error, commands.BadArgument):
            embed = create_embed(
                color="red",
                title=_("errors.bad_argument.title", ctx),
                desc=_("errors.bad_argument.desc", ctx, cmd_name=ctx.command.name, cmd_usage=ctx.command.usage),
                thumnail=get_emote('no', return_return_type='image')
            )
            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                content=_("errors.cooldown", ctx, emote=get_emote("warning"), time_left=round(error.retry_after)),
                mention_author=False,
                delete_after=error.retry_after
            )


def setup(gigachad):
    gigachad.add_cog(ErrorHandler(gigachad))
