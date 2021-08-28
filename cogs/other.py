import asyncio
import json
import os

import aiohttp
import discord
from cogs.prefix import get_prefix
from discord.ext import commands
from util.misc import get_emote, create_embed
from util.misc import translate as _

WATCHBOT_API_KEY = os.getenv("WATCHBOT_API_KEY")


class Other(commands.Cog):
    """
    All the other stuff that doesn't go in other Cogs!
    """

    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.command(
        name="support",
        usage="support",
        description="Get an invite to the support server"
    )
    async def support(self, ctx):
        embed = create_embed(
            title=_("info.support.title", ctx, emote=get_emote("sos")),
            desc=_("info.support.desc", ctx)
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(
        name="invite",
        usage="invite",
        description="Get the link to invite Giga Chad"
    )
    async def invite(self, ctx):
        embed = create_embed(
            title=_("info.invite.title", ctx, emote=get_emote("invite")),
            desc=_("info.invite.desc", ctx, invite_link=self.gigachad.invite_link),
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="vote", usage="vote", description="Get the link to vote for GigaChad")
    async def vote(self, ctx):
        embed = create_embed(
            title=_("info.vote.title", ctx, emote=get_emote("vote")),
            desc=_("info.vote.desc", ctx)
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(
        name="info",
        usage="info",
        aliases=["about"],
        description="Get useful information about Giga Chad"
    )
    async def info(self, ctx):
        embed = create_embed(
            title=_("info.info.title", ctx, emote=get_emote("gigachad")),
            desc=_("info.info.desc", ctx, emote=get_emote("python")),
            fields=[
                [_("info.info.version.title", ctx, emote=get_emote("info")),
                 "`•` Giga Chad Bot `v1.0`", True],
                [_("info.info.stats.title", ctx, emote=get_emote("stats")),
                 _("info.info.stats.desc", ctx, nb=str(len(self.gigachad.guilds))), True],
                [_("info.info.ping.title", ctx, emote=get_emote("ping")),
                 _("info.info.ping.desc", ctx, time=round(self.gigachad.latency * 1000)), True],
                [_("info.support.title", ctx, emote=get_emote("sos")),
                 _("info.support.desc", ctx), True],
                [_("info.invite.title", ctx, emote=get_emote("invite")),
                 _("info.invite.desc", ctx, invite_link=self.gigachad.invite_link), True],
                [_("info.info.credits.title", ctx, emote=get_emote("copyright")),
                 _("info.info.credits.desc", ctx), True],
                [_("info.info.docs.title", ctx, emote=get_emote("docs")),
                 _("info.info.docs.desc", ctx), True],
                [_("info.info.source.title", ctx, emote=get_emote("github")),
                 _("info.info.source.desc", ctx), True],
                [_("info.vote.title", ctx, emote=get_emote("vote")),
                 _("info.vote.desc", ctx), True],
                [_("info.info.uptime.title", ctx, emote=get_emote("uptime")),
                 _("info.info.uptime.loading", ctx, emote=get_emote("loading"))]
            ],
            footer_text=_("info.info.footer", ctx)
        )
        message = await ctx.reply(embed=embed, mention_author=False)
        embed.set_field_at(
            index=9,
            name=_("info.info.uptime.title", ctx, emote=get_emote("uptime")),
            value=await get_uptime(ctx),
            inline=False
        )
        await message.edit(embed=embed)

    @commands.command(
        name="prefix",
        usage="prefix [new prefix]",
        description=f"Change the guild prefix. Requires the user to have {get_emote('role')} "
                    "`MANAGE_SERVER` permission"
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def prefix(self, ctx, prefix=None):

        if prefix is None:

            current_prefix = get_prefix(self.gigachad, ctx, True)
            embed = create_embed(
                title=_("info.prefix.current.title", ctx),
                desc=_("info.prefix.current.desc", ctx, prefix=current_prefix)
            )

        else:

            if prefix == "gc!":

                current_prefix = get_prefix(self.gigachad, ctx, True)
                embed = create_embed(
                    title=_("info.prefix.failure.default.title", ctx),
                    desc=_("info.prefix.failure.default.desc", ctx, prefix=current_prefix),
                    thumbnail="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32",
                    color="red"
                )

            else:

                if prefix == "reset":

                    if ctx.guild.id in self.gigachad.prefix_cache:

                        async with self.gigachad.db.acquire() as conn:
                            await conn.execute("DELETE FROM prefixes WHERE guild = $1", ctx.guild.id)

                        self.gigachad.prefix_cache.pop(ctx.guild.id)

                        embed = create_embed(
                            color="green",
                            title=_("info.prefix.success.reset.title", ctx),
                            desc=_("info.prefix.success.reset.desc", ctx),
                            thumbnail="https://cdn.discordapp.com/emojis/847027842637103134.png?size=32"
                        )

                    else:
                        print("guild id is not in cache")
                        print(ctx.guild.id)

                        embed = create_embed(
                            color="red",
                            title=_("info.prefix.failure.reset.title", ctx),
                            desc=_("info.prefix.failure.reset.desc", ctx),
                            thumbnail="https://cdn.discordapp.com/emojis/847027842365915167.png?size=32"
                        )

                else:

                    self.gigachad.prefix_cache[ctx.guild.id] = prefix

                    async with self.gigachad.db.acquire() as conn:
                        await conn.execute("INSERT INTO prefixes (guild, prefix) VALUES ($1, $2) "
                                           "ON CONFLICT(guild) "
                                           "DO UPDATE SET prefix = $2 ", ctx.guild.id, prefix)

                    embed = create_embed(
                        color="green",
                        title=_("info.prefix.success.changed.title", ctx),
                        desc=_("info.prefix.success.changed.desc", ctx, prefix=prefix),
                        thumbnail="https://cdn.discordapp.com/emojis/847027842637103134.png?size=32"
                    )

        await ctx.reply(
            embed=embed,
            mention_author=False
        )

    @commands.command(
        name="slash",
        usage="slash",
        description="A guide to help if slash commands aren't working"
    )
    async def slash(self, ctx):
        embed = create_embed(
            title=get_emote("slash") + " Slash Commands Troubleshooting",
            desc="There might be a few different reasons on why the slash commands aren't working. Here is a list of "
                 "them:",
            fields=[
                ["Wrong Permissions",
                 "`•` Make sure that you/bot users have permissions to use slash commands in the apropriate channel",
                 True],
                ["Wrong Invites",
                 "`•` The bot might have been invited with the wrong invite. Click [here]("
                 "https://invite.gigachad-bot.xyz) to invite the bot again", True],
                ["Support Server",
                 "`•` If none of the above solutions worked, click [here](https://links.gigachad-bot.xyz/support) to "
                 "join the support server and get further help ", True]
            ]
        )
        await ctx.reply(embed=embed, mention_author=False)


async def get_uptime(ctx):
    try:
        headers = {"AUTH-TOKEN": WATCHBOT_API_KEY}
        url = "https://api.watchbot.app/bot/843550872293867570"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as r:
                data = await r.read()
        json_data = json.loads(data)
        return _("info.info.uptime.success", ctx, week=json_data['7d'], month=json_data['30d'], months=json_data['90d'])

    except:
        return _("info.info.uptime.failure", ctx, emote=get_emote("no"))


def setup(gigachad):
    gigachad.add_cog(Other(gigachad))
