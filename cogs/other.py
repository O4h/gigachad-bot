import asyncio
import json
import os

import aiohttp
import disnake
from disnake.ext import commands
from util.misc import get_emote, create_embed
from util.misc import translate as _

WATCHBOT_API_KEY = os.getenv("WATCHBOT_API_KEY")


class Other(commands.Cog):
    """
    All the other stuff that doesn't go in other Cogs!
    """

    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.slash_command()
    async def vote(self, ctx: disnake.ApplicationCommandInteraction):
        """
        Get the link to vote for GigaChad

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        """

        embed = create_embed(
            title=_("info.vote.title", ctx, emote=get_emote("vote")),
            desc=_("info.vote.desc", ctx)
        )
        await ctx.send(embed=embed)

    @commands.slash_command()
    async def info(self, ctx: disnake.ApplicationCommandInteraction):
        """
        Get useful information about Giga Chad

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        """
        embed = create_embed(
            title=_("info.info.title", ctx, emote=get_emote("gigachad")),
            desc=_("info.info.desc", ctx, dot=get_emote("dot"), emote=get_emote("python")),
            fields=[
                (_("info.info.version.title", ctx, emote=get_emote("info")),
                 get_emote('dot') + " Giga Chad Bot `v1.0`", True),
                (_("info.info.stats.title", ctx, emote=get_emote("stats")),
                 get_emote('dot') + _("info.info.stats.desc", ctx, nb=str(len(self.gigachad.guilds))), True),
                (_("info.info.ping.title", ctx, emote=get_emote("ping")),
                 get_emote('dot') + _("info.info.ping.desc", ctx, time=round(self.gigachad.latency * 1000)), True),
                (_("info.support.title", ctx, emote=get_emote("sos")),
                 get_emote('dot') + _("info.support.desc", ctx), True),
                (_("info.invite.title", ctx, emote=get_emote("invite")),
                 get_emote('dot') + _("info.invite.desc", ctx, invite_link=self.gigachad.invite_link), True),
                (_("info.vote.title", ctx, emote=get_emote("vote")),
                 get_emote('dot') + _("info.vote.desc", ctx), True),
                (_("info.info.docs.title", ctx, emote=get_emote("docs")),
                 get_emote('dot') + _("info.info.docs.desc", ctx), True),
                (_("info.info.source.title", ctx, emote=get_emote("github")),
                 get_emote('dot') + _("info.info.source.desc", ctx), True),
                (_("info.info.credits.title", ctx, emote=get_emote("copyright")),
                 get_emote('dot') + _("info.info.credits.desc", ctx, emote=get_emote('dot')), True),
                (_("info.info.uptime.title", ctx, emote=get_emote("uptime")),
                 get_emote('dot') + _("info.info.uptime.loading", ctx, emote=get_emote("loading")))
            ],
            footer_text=_("info.info.footer", ctx),
            image="https://i.imgur.com/MiVm8av.png"
        )
        await ctx.send(embed=embed)
        embed.set_field_at(
            index=9,
            name=_("info.info.uptime.title", ctx, emote=get_emote("uptime")),
            value=await get_uptime(ctx),
            inline=False
        )
        await ctx.edit_original_message(embed=embed)


async def get_uptime(ctx):
    """"
    Get the uptime of the bot from the watchbot API

    Parameters
    ----------
    ctx : disnake.ext.commands.Context
        The context where the command was called
    """
    headers = {"AUTH-TOKEN": WATCHBOT_API_KEY}
    url = "https://api.watchbot.app/bot/843550872293867570"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            data = await r.read()
    if r.status != 200:
        return _(
            "info.info.uptime.failure", ctx, emote=get_emote("no"), dot=get_emote("dot")
        )
    json_data = json.loads(data)
    return _(
        "info.info.uptime.success",
        ctx,
        emote=get_emote("dot"),
        week=json_data["7d"],
        month=json_data["30d"],
        months=json_data["90d"],
    )


def setup(gigachad):
    gigachad.add_cog(Other(gigachad))
