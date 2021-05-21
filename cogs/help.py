import discord
from discord.ext import commands


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
        embed = discord.Embed(title="<:gigachad:843818002616418367> Giga Chad Info", color=0x2f3136,
                              description="Giga Chad is a bot written in Python <:python:844904483946364935> by "
                                          "`Thorgal#0982` using the discord.py and discord-py-slash-command librairies.")
        embed.add_field(name="Credits", value="`•` The GigaChadBot profile picture and images are from [@berlin.1969]"
                                              "(https://www.instagram.com/berlin.1969/)'s instagram.", inline=False)
        embed.add_field(name="APIs", value="`•` [imgflip.com](https://imgflip.com/)'s API \n `•` [reddit.com]("
                                           "https://www.reddit.com/)'s API", inline=False)
        embed.set_footer(text="DM Thorgal#0982 for further information")
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="<:gigachad:843818002616418367> Giga Chad Help", color=0x2f3136)
        embed.add_field(name="<:slash:844135268806426636> Slash Commands",
                        value="Most of the Giga Chad's commands are [slash commands]("
                              "https://support.discord.com/hc/fr/articles/1500000368501-Slash-Commands-FAQ). Click the "
                              "blue link if you don't know what those are and how to use them. If the slash commands "
                              "don't show up, check if users have the permission to use them, or kick then re-invite the "
                              "bot using [this](link). \n Simply type a `/` to get the list of slash commands and their "
                              "description!", inline=False)
        embed.add_field(name="Other Commands", value="`•` `gc!help` **-** That's the command you're using right now \n "
                                                     "`•` `gc!info` **-** Get info about the vote \n `•` `gc!invite` **-** "
                                                     "Invite the bot to another server")
        embed.set_footer(text="DM Thorgal#0982 for further help")
        await ctx.send(embed=embed)


def setup(gigachad):
    gigachad.add_cog(Help(gigachad))
