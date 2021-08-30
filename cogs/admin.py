import asyncio
import datetime
import os
import time
import traceback
import discord
import psutil
import json

from discord.ext import commands
from util.misc import get_emote, create_embed

start_time = time.time()


class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, gigachad):
        """ A cog with stricly admin-only cmds """
        self.gigachad = gigachad

    @commands.command(name="astats", usage="astats")
    @commands.is_owner()
    async def astats(self, ctx):
        embed = create_embed(
            title=f"{get_emote('admin')}  **Advanced admin stats**",
            fields=[
                ["Uptime",
                 f"`•` Online since <t:{int(round(start_time))}:F> \n  `•` Online since <t:{int(round(start_time))}:R>",
                 True],
                ["Hardware Stats",
                 f"`•` CPU `{str(psutil.cpu_percent(interval=1))}%` \n `•` RAM `{str(psutil.virtual_memory().percent)}%`",
                 True]
            ]
        )
        await ctx.reply(embed=embed, mention_author=False)


def setup(gigachad):
    gigachad.add_cog(Admin(gigachad))
