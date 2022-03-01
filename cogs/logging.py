import os
import time

import aiohttp
import disnake
from disnake.ext import commands, tasks
from util.misc import create_embed, get_emote

log_channel = int(os.getenv("LOG_CHANNEL"))
ignored_users = os.getenv("LOGS_IGNORED_USERS")

beta = bool(os.getenv("BETA") == "TRUE")


async def log_cmd(bot: commands.AutoShardedBot, name, ctx, cmd_type: int) -> None:
    """
    Log commands uses

    Parameters
    ----------
    bot : commands.AutoShardedBot
        The bot instance
    name : str
        The name of the command
    ctx : commands.Context
        The context of the command
    cmd_type : int
        The type of the command, 1 for normal commands, 2 for slash commands, 3 for context menus
    """
    if str(ctx.author.id) in ignored_users:
        return

    guild = ctx.author.id if ctx.guild is None else ctx.guild.id

    async with bot.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO commands_logs (time, guild, cmd, usr, type) "
            "VALUES ($1, $2, $3, $4, $5)",
            round(time.time()),
            guild,
            name.name,
            ctx.author.id,
            cmd_type,
        )


async def log_guild(
    bot: commands.AutoShardedBot, guild: disnake.Guild, joined: bool
) -> None:
    """
    Log guilds join and leave events

    Parameters
    ----------
    bot : commands.AutoShardedBot
        The bot instance
    guild : disnake.Guild
        The guild that is being joined or left
    joined : bool
        True if the guild is being joined, False if it is being left
    """
    async with bot.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO guilds_logs (time, guild, joined, guild_count) "
            "VALUES ($1, $2, $3, $4)",
            round(time.time()),
            guild.id,
            joined,
            len(bot.guilds),
        )


class Logging(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        """
        Log stats about the bot for better understanding of users utilisations
        """
        self.bot = bot

        self.commands_stats_update.start()
        if not beta:
            self.topgg_stats_update.start()  # start the top.gg automatic stats updates

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild) -> None:
        """
        Send embed and log on guild join

        Parameters
        ----------
        guild : disnake.Guild
            The guild that the bot just joined
        """
        await log_guild(self.bot, guild, True)
        owner = await self.bot.fetch_user(guild.owner_id)
        embed = create_embed(
            title=f"Joined Guild {guild.name}",
            desc=f"`•` Owner: `{owner.name}#{owner.discriminator}` \n"
            f"`•` Members: `{guild.member_count}` \n "
            f"`•` `{len(self.bot.guilds)}th` guild ",
            thumbnail=guild.icon_url,
            footer_text=guild.id,
            color="green",
        )
        chan = await self.bot.fetch_channel(log_channel)
        await chan.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild) -> None:
        """
        Send embed and log on guild leave

        Parameters
        ----------
        guild : disnake.Guild
            The guild that the bot just left
        """
        await log_guild(self.bot, guild, False)
        owner = await self.bot.fetch_user(guild.owner_id)
        embed = create_embed(
            title=f"Left Guild {guild.name}",
            desc=f"`•` Owner: `{owner.name}#{owner.discriminator}` \n"
            f"`•` Members: `{guild.member_count}`\n "
            f"`•` `{len(self.bot.guilds)}` guilds left ",
            thumbnail=guild.icon_url,
            footer_text=guild.id,
            color="red",
        )

        chan = await self.bot.fetch_channel(log_channel)
        await chan.send(embed=embed)

    @commands.Cog.listener()
    async def on_command(self, ctx) -> None:
        """Log command"""
        await log_cmd(self.bot, ctx.command, ctx, 1)

    @commands.Cog.listener()
    async def on_slash_command(self, ctx) -> None:
        """Log slash commands"""
        await log_cmd(self.bot, ctx, ctx, 2)

    @tasks.loop(minutes=30)
    async def topgg_stats_update(self) -> None:
        """
        Automatically update server stats on top.gg
        """
        headers = {"Authorization": os.getenv("TOPGG_TOKEN")}
        url = "https://top.gg/api/bots/843550872293867570/stats"
        body = {"server_count": len(self.bot.guilds)}
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, headers=headers, data=body) as response:
                if response.status == 200:
                    print(f"Stats Posted! {self.bot.user}")

                else:
                    print(f"Error while posting stats: {await response.read()}")

    @tasks.loop(minutes=10)
    async def commands_stats_update(self) -> None:
        """
        Update command stats to db
        """
        values_to_insert = {}
        async with self.bot.db.acquire() as conn:
            for commands in self.bot.command_list.keys():
                values_to_insert[commands] = 0
                for command_alias in self.bot.command_list[commands]:
                    temp_value = await conn.fetchrow(
                        "SELECT COUNT(*) FROM commands_logs WHERE cmd = $1",
                        command_alias,
                    )
                    values_to_insert[commands] += dict(temp_value)["count"]
            await conn.execute(
                "INSERT INTO commands_stats_total (time, gallery, gigachadify, meme, caption, chadmeter)"
                " VALUES ($1, $2, $3, $4, $5, $6)",
                round(time.time()),
                values_to_insert["gallery"],
                values_to_insert["gigachadify"],
                values_to_insert["meme"],
                values_to_insert["caption"],
                values_to_insert["chadmeter"],
            )

    @commands_stats_update.before_loop
    async def before_commands_stats_update(self) -> None:
        """
        Makes sure that the loop waits until the bot is ready before trying to post stats
        """
        await self.bot.wait_until_ready()

    @topgg_stats_update.before_loop
    async def before_topgg_stats_update(self) -> None:
        """
        Makes sure that the loop waits until the bot is ready before trying to post stats
        """
        await self.bot.wait_until_ready()


def setup(bot: commands.AutoShardedBot) -> None:
    bot.add_cog(Logging(bot))
