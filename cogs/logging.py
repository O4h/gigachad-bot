import os
import time

import aiohttp
import disnake
from disnake.ext import commands, tasks
from util.misc import create_embed

log_channel = int(os.getenv("LOG_CHANNEL"))
beta = os.getenv("BETA") == "TRUE"


class Logging(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        """
        Log stats about the bot for better understanding of users utilisations
        """
        self.bot = bot

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
        owner = await self.bot.fetch_user(guild.owner_id)
        embed = create_embed(
            title=f"Joined Guild {guild.name}",
            desc=f"`•` Owner: `{owner.name}#{owner.discriminator}` \n"
                 f"`•` Members: `{guild.member_count}` \n "
                 f"`•` `{len(self.bot.guilds)}th` guild ",
            thumbnail=guild.icon.url,
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
        owner = await self.bot.fetch_user(guild.owner_id)
        embed = create_embed(
            title=f"Left Guild {guild.name}",
            desc=f"`•` Owner: `{owner.name}#{owner.discriminator}` \n"
                 f"`•` Members: `{guild.member_count}`\n "
                 f"`•` `{len(self.bot.guilds)}` guilds left ",
            thumbnail=guild.icon.url,
            footer_text=guild.id,
            color="red",
        )

        chan = await self.bot.fetch_channel(log_channel)
        await chan.send(embed=embed)

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

    @topgg_stats_update.before_loop
    async def before_topgg_stats_update(self) -> None:
        """
        Makes sure that the loop waits until the bot is ready before trying to post stats
        """
        await self.bot.wait_until_ready()


def setup(bot: commands.AutoShardedBot) -> None:
    bot.add_cog(Logging(bot))
