import discord
import asyncio
import os
import requests
from dotenv import load_dotenv
from discord.ext import commands
from cogs.prefix import get_prefix

load_dotenv()
WATCHBOT_API_KEY = os.getenv("WATCHBOT_API_KEY")


class Help(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.command()
    async def support(self, ctx):
        embed = discord.Embed(title="Test")
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(title="Invite Giga Chad!", color=0x2f3136,
                              description="Click [here](https://discord.com/api/oauth2/authorize?client_id"
                                          f"={str(self.gigachad.user.id)}&permissions=2147551232&scope=bot"
                                          f"%20applications.commands) to invite Giga Chad!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['about'])
    async def info(self, ctx):
        embed = discord.Embed(title="<:gigachad:845633149923753984> Giga Chad Info", color=0x2f3136,
                              description="Giga Chad is a bot written in Python <:python:846068944514711612> by "
                                          "`Thorgal#0982` using the discord.py and discord-py-slash-command "
                                          "librairies.")
        embed.add_field(name="<:gc_info:847034105026838569> Version", value="`•` Giga Chad Bot `v1.0`", inline=True)
        embed.add_field(name="<:gc_stats:847029255178944532> Stats",
                        value=f"`•` {str(len(self.gigachad.guilds))} Servers")
        embed.add_field(name="<:gc_ping:847031168015794176> Ping",
                        value=f"`•` `{round(self.gigachad.latency * 1000)}ms`", inline=True)
        embed.add_field(name="<:gc_help:847030094417625108> Support Server",
                        value="`•` Click [here](https://discord.gg/atPkjGgDBD) to join", inline=True)
        embed.add_field(name="<:gc_invite:847035767519707136> Invite",
                        value="`•` Click [here](https://discord.com/api/oauth2/authorize?client_id"
                              f"{str(self.gigachad.user.id)}&permissions=2147551232&scope=bot%20applications.commands"
                              ") to invite", inline=True)
        embed.add_field(name="<:gc_copyright:847029255254310933> Credits",
                        value="`•` [@berlin.1969](https://www.instagram.com/berlin.1969/) \n `•` ["
                              "flaticon.com](https://www.flaticon.com/)",
                        inline=True)
        try:
            headers = {"AUTH-TOKEN": WATCHBOT_API_KEY}
            r = requests.get(f"https://api.watchbot.app/bot/{str(self.gigachad.user.id)}", headers=headers)
            r_dictionnary = r.json()
            _7d = r_dictionnary['7d']
            _30d = r_dictionnary['30d']
            _90d = r_dictionnary['90d']
            embed.add_field(name="<:gc_uptime:847029255225344020> Uptime",
                            value=f"`•` Click [here](https://status.watchbot.app/bot/"
                                  f"{str(self.gigachad.user.id)}) to access the bot's uptime history\n - "
                                  f"Over the last week: `{_7d}%` uptime \n - Over the last month: `"
                                  f"{_30d}%` uptime \n - Over the last 90 days: `{_90d}% uptime`",
                            inline=False)
        except:
            embed.add_field(name="<:gc_uptime:847029255225344020> Uptime",
                            value=f"`•` <:gc_no:847027842365915167> Something went wrong, the bot wasn't able to "
                                  f"retrieve its uptime.",
                            inline=False)
        embed.set_footer(text="Join the suppport server for further information")
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        prefix = get_prefix(self, ctx, True)
        embed = discord.Embed(title="<:gigachad:845633149923753984> Giga Chad Help", color=0x2f3136)
        embed.add_field(name="<:slash:845659423569477632> Slash Commands",
                        value="`•` Most of the Giga Chad's commands are [slash commands]("
                              "https://support.discord.com/hc/fr/articles/1500000368501-Slash-Commands-FAQ). Click "
                              "the blue link if you don't know what those are and how to use them. If the slash "
                              "commands don't show up, check if users have the permission to use them, or kick then "
                              "re-invite the bot using [this](https://discord.com/api/oauth2/authorize?client_id"
                              f"={str(self.gigachad.user.id)}&permissions=2147551232&scope=bot%20applications"
                              ".commands) link. The list of the available slash commands and "
                              "their description can be found [here](https://discordbotlist.com/bots/giga-chad).",
                        inline=False)
        embed.add_field(name="<:settings:845659423561089034> Other Commands",
                        value=f"`•` `{prefix}help` **-** That's the command you're using right now \n `•` `{prefix}in"
                              f"fo` **-** Get info about the vote \n `•` `{prefix}invite` **-** Invite the bot to "
                              f"another server \n `•` `{prefix}support` **-** Get an invite to the support server \n "
                              f"`•` `{prefix}prefix [new prefix]` **-** Change the bot prefix",
                        inline=False)
        embed.set_footer(text=f"Join the support server ({prefix}support) for further help")
        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        embed = discord.Embed(title="Support Server", color=0x2f3136,
                              description="Click [here](https://discord.gg/atPkjGgDBD) to access the support server")
        await ctx.send(embed=embed)


def setup(gigachad):
    gigachad.add_cog(Help(gigachad))
