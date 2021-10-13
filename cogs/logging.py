import os
import time

import aiohttp
import discord
from discord.ext import commands, tasks
from util.misc import create_embed, get_emote

log_channel = os.getenv("LOG_CHANNEL")
ignored_users = os.getenv("LOGS_IGNORED_USERS")

beta = True if os.getenv("BETA") == "TRUE" else False


async def log_cmd(gigachad: commands.Bot, name, ctx, cmd_type: int):
    """ Log commands uses
    :param cmd_type: is used to log whether the logged cmd
    was a normal command (-> type 1), a slash command (-> type 2)
    or a context menu command (-> type 3) """
    if str(ctx.author.id) in ignored_users:
        return
    if ctx.guild is None:
        guild = ctx.author.id

    else:
        guild = ctx.guild.id

    async with gigachad.db.acquire() as conn:
        await conn.execute("INSERT INTO commands_logs (time, guild, cmd, usr, type) "
                           "VALUES ($1, $2, $3, $4, $5)",
                           round(time.time()), guild, name.name, ctx.author.id, cmd_type)


async def log_guild(gigachad: commands.Bot, guild: discord.Guild, joined: bool):
    """ Log guilds join and leave events,
    if :param joined: is True then it joined a guild,
    if False it left it """
    async with gigachad.db.acquire() as conn:
        await conn.execute("INSERT INTO guilds_logs (time, guild, joined) "
                           "VALUES ($1, $2, $3)",
                           round(time.time()), guild.id, joined)


class Logging(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, gigachad):
        """ Log stats about the bot for better understanding of users utilisations """
        self.gigachad = gigachad
        
        if not beta:
            self.topgg_stats_update.start()  # start the top.gg automatic stats updates

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """ Send embed and log on guild join"""
        await log_guild(self.gigachad, guild, True)
        owner = await self.gigachad.fetch_user(guild.owner_id)
        embed = create_embed(
            title=f"Joined Guild {guild.name}",
            desc=f"`•` Owner: `{owner.name}#{owner.discriminator}` \n`•` Members: `{guild.member_count}` "
                 f"\n `•` `{str(len(self.gigachad.guilds))}th` guild ",
            thumbnail=guild.icon_url,
            footer_text=guild.id,
            color="green"
        )
        chan = await self.gigachad.fetch_channel(log_channel)
        await chan.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """ Send embed and log on guild leave"""
        await log_guild(self.gigachad, guild, False)
        owner = await self.gigachad.fetch_user(guild.owner_id)
        embed = create_embed(
            title=f"Left Guild {guild.name}",
            desc=f"`•` Owner: `{owner.name}#{owner.discriminator}` \n`•` Members: `{guild.member_count}`"
                 f"\n `•` `{str(len(self.gigachad.guilds))}` guilds left ",
            thumbnail=guild.icon_url,
            footer_text=guild.id,
            color="red"
        )
        chan = await self.gigachad.fetch_channel(log_channel)
        await chan.send(embed=embed)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """ Log command """
        await log_cmd(self.gigachad, ctx.command, ctx, 1)

    @commands.Cog.listener()
    async def on_slash_command(self, ctx):
        """ Log slash commands """
        await log_cmd(self.gigachad, ctx, ctx, 2)

    @tasks.loop(minutes=30)
    async def topgg_stats_update(self):
        """ Automatically update stats on top.gg"""
        headers = {"Authorization": os.getenv("TOPGG_TOKEN")}
        url = "https://top.gg/api/bots/843550872293867570/stats"
        body = {"server_count": len(self.gigachad.guilds)}
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, headers=headers, data=body) as response:
                if response.status == 200:
                    print(f"Stats Posted! {self.gigachad.user}")
                else:
                    print(f"Error while posting stats: {await response.read()}")

    @topgg_stats_update.before_loop
    async def before_topgg_stats_update(self):
        """ Make sure that the loop waits until
        the bot is ready before trying to post
        stats """
        await self.gigachad.wait_until_ready()


def setup(gigachad):
    gigachad.add_cog(Logging(gigachad))
