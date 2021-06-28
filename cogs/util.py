import discord
import asyncio
import os
import aiohttp
import json

from dotenv import load_dotenv
from discord.ext import commands
from cogs.prefix import get_prefix
from util.emotes import get_emote

WATCHBOT_API_KEY = os.getenv("WATCHBOT_API_KEY")


class Other(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.command(
                      name="support",
                      usage="support",
                      description="Get an invite to the support server"
                      )
    async def support(self, ctx):
        embed = discord.Embed(
                              title="Support Server",
                              color=0x2f3136,
                              description="Click [here](https://discord.gg/atPkjGgDBD) to access the support server"
                             )
        await ctx.reply(
                        embed=embed,
                        mention_author=False
                        )

    @commands.command(
                      name="invite",
                      usage="invite",
                      description="Get the link to invite Giga Chad"
                      )
    async def invite(self, ctx):
        embed = discord.Embed(
                              title=get_emote("invite") + "Invite Giga Chad!",
                              color=0x2f3136,
                              description="Click [here](https://discord.com/api/oauth2/authorize?client_id"
                                          f"={str(self.gigachad.user.id)}&permissions=346112&scope=bot"
                                          f"%20applications.commands) to invite Giga Chad!"
                              )
        await ctx.reply(
                        embed=embed,
                        mention_author=False
                        )

    @commands.command(
                      name="info",
                      usage="info",
                      aliases=["about"],
                      description="Get useful information about Giga Chad"
                     )
    async def info(self, ctx):
        embed = discord.Embed(
                              title=get_emote("gigachad") + " Giga Chad Info",
                              color=0x2f3136,
                              description=f"Giga Chad is a bot written in Python {get_emote('python')} by "
                                          "`Orh#0982` using the discord.py and discord-py-slash-command "
                                          "librairies."
                              )
        embed.add_field(
                        name=get_emote("info") + " Version",
                        value="`•` Giga Chad Bot `v1.0`",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("stats") + " Stats",
                        value=f"`•` {str(len(self.gigachad.guilds))} Servers",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("ping") + " Ping",
                        value=f"`•` `{round(self.gigachad.latency * 1000)}ms`",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("sos") + " Support Server",
                        value="`•` Click [here](https://discord.gg/atPkjGgDBD) to join",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("invite") + " Invite",
                        value="`•` Click [here](https://discord.com/api/oauth2/authorize?client_id"
                              f"{str(self.gigachad.user.id)}&permissions=346112&scope=bot%20applications.commands"
                              ") to invite",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("copyright") + " Credits",
                        value="`•` [@berlin.1969](https://www.instagram.com/berlin.1969/) \n `•` ["
                              "flaticon.com](https://www.flaticon.com/)",
                        inline=True)
        embed.add_field(
                        name=get_emote("docs") + " Docs",
                        value="`•` Click [here](https://docs.gigachad-bot.xyz/) to see the docs",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("github") + " Source Code",
                        value="`•` Click [here](https://github.com/thorgal108/gigachad-bot) to see the bot's source "
                              "code ",
                        inline=True
                        )
        embed.add_field(
                        name=get_emote("uptime") + " Uptime",
                        value="Loading..." + get_emote('loading'),
                        inline=False
                        )
        embed.set_footer(
                        text="Join the suppport server for further information"
                         )
        message = await ctx.reply(
                                  embed=embed,
                                  mention_author=False
                                  )
        embed.set_field_at(
                           index=8,
                           name=get_emote("uptime") + " Uptime",
                           value=await get_uptime(),
                           inline=False
                            )
        await message.edit(
                           embed=embed
                            )

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
            current_prefix = get_prefix(self, ctx, True)
            embed = discord.Embed(
                                  color=0x2f3136,
                                  title="Current Prefix",
                                  description=f"My current prefix is `{current_prefix}`. \n Execute `{current_prefix}pr"
                                              "efix [newprefix]` to set a new prefix!"
                                  )

        else:
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)

            prefixes[str(ctx.guild.id)] = prefix

            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)

            embed = discord.Embed(
                                  color=0x57f287,
                                  title="Prefix succesfully changed",
                                  description=f"My prefix for this server has succefully been changed to `{prefix}`."
                                 )
            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/emojis/847027842637103134.png?size=32"
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
        embed = discord.Embed(
                              title=get_emote("slash") + " Slash Commands Troubleshooting",
                              color=0x2f3136,
                              description="There might be a few different reasons on why the slash commands aren't "
                                          "working. Here is a list of them:"
                              )
        embed.add_field(
                        name="Wrong Permissions",
                        value="`•` Make sure that you/bot users have permissions to use slash commands in the "
                              "apropriate channel"
                        )
        embed.add_field(
                        name="Wrong Invites",
                        value="`•` The bot might have been invited with the wrong invite. Click [here](https://invite.g"
                              "igachad-bot.xyz) to invite the bot again"
                        )
        embed.add_field(
                        name="Support Server",
                        value="`•` If none of the above solutions worked, click [here]("
                              "http://links.gigachad-bot.xyz/support) to join the support server and get further help"

                        )
        await ctx.reply(
                        embed=embed,
                        mention_author=False
                        )


async def get_uptime():
    try:
        headers = {"AUTH-TOKEN": WATCHBOT_API_KEY}
        url = f"https://api.watchbot.app/bot/843550872293867570"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as r:
                data = await r.read()
        json_data = json.loads(data)
        return f"`•` Click [here](https://status.gigachad-bot.xyz/) to access the bot's uptime history\n - Over the " \
               f"last week: `{json_data['7d']}%` uptime \n - Over the last month: `{json_data['30d']}%` uptime \n - " \
               f"Over the last 90 days: `{json_data['90d']}% uptime` "

    except:
        return f"`•` {get_emote('no')} Something went wrong, the bot wasn't able to retrieve its uptime. \n " \
               "`•` Click [here](https://status.gigachad-bot.xyz/) to acess the bot's detailed uptime"


def setup(gigachad):
    gigachad.add_cog(Other(gigachad))
