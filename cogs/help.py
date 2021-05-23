import discord
import asyncio
import os
import requests
from dotenv import load_dotenv
from discord.ext import commands

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
                                          "=843550872293867570&permissions=2147551232&scope=bot%20applications"
                                          ".commands) "
                                          "to invite Giga Chad!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['about'])
    async def info(self, ctx):
        embed = discord.Embed(title="<:gigachad:845633149923753984> Giga Chad Info", color=0x2f3136,
                              description="Giga Chad is a bot written in Python <:python:846068944514711612> by "
                                          "`Thorgal#0982` using the discord.py and discord-py-slash-command "
                                          "librairies.")
        embed.add_field(name="Credits", value="`•` The GigaChadBot profile picture and images are from [@berlin.1969]"
                                              "(https://www.instagram.com/berlin.1969/)'s instagram.", inline=False)
        embed.add_field(name="APIs", value="`•` [imgflip.com](https://imgflip.com/)'s API \n `•` [reddit.com]("
                                           "https://www.reddit.com/)'s API", inline=False)
        embed.add_field(name="Ping", value=f"`•` `{round(self.gigachad.latency * 1000)}ms`")
        headers = {"AUTH-TOKEN": WATCHBOT_API_KEY}
        r = requests.get(f"https://api.watchbot.app/bot/{int(self.gigachad.user.id)}", headers=headers)
        r_dictionnary = r.json()
        _7d = r_dictionnary['7d']
        _30d = r_dictionnary['30d']
        _90d = r_dictionnary['90d']
        embed.add_field(name="Status", value="`•` Click [here](https://status.watchbot.app/bot/843550872293867570) to "
                                             f"access the bot's uptime history\n - Over the "
                                             f"last week: `{_7d}%` uptime \n - Over the last month: `{_30d}%` uptime "
                                             f"\n - Over the last 90 days: `{_90d}% uptime`", inline=False)
        embed.add_field(name="Support Server", value="`•` Click [here](https://discord.gg/atPkjGgDBD) to access the "
                                                     "support server", inline=False)
        embed.set_footer(text="Join the suppport server for further information")
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="<:gigachad:845633149923753984> Giga Chad Help", color=0x2f3136)
        embed.add_field(name="<:slash:845659423569477632> Slash Commands",
                        value="Most of the Giga Chad's commands are [slash commands]("
                              "https://support.discord.com/hc/fr/articles/1500000368501-Slash-Commands-FAQ). Click "
                              "the blue link if you don't know what those are and how to use them. If the slash "
                              "commands don't show up, check if users have the permission to use them, or kick then "
                              "re-invite the bot using [this](https://discord.com/api/oauth2/authorize?client_id"
                              "=843550872293867570&permissions=2147551232&scope=bot%20applications"
                              ".commands) link. The list of the available slash commands and "
                              "their description can be found [here](https://discordbotlist.com/bots/giga-chad).",
                        inline=False)
        embed.add_field(name="<:settings:845659423561089034> Other Commands",
                        value="`•` `gc!help` **-** That's the command you're using right now \n `•` `gc!info` **-** "
                              "Get info about the vote \n `•` `gc!invite` **-** Invite the bot to another server \n "
                              "`•` `gc!support` **-** Get an invite to the support server", inline=False)
        embed.set_footer(text="Join the support server (gc!support) for further information")
        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        embed = discord.Embed(title="Support Server", color=0x2f3136,
                              description="Click [here](https://discord.gg/atPkjGgDBD) to access the support server")
        await ctx.send(embed=embed)


def setup(gigachad):
    gigachad.add_cog(Help(gigachad))
