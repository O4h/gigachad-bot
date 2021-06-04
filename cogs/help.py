import discord
import asyncio
from discord.ext import commands
from cogs.prefix import get_prefix


class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        prefix = get_prefix(self, self.context, True)
        fun_cog = self.context.bot.get_cog('Fun')
        fun_cmds_list = fun_cog.get_commands()
        fun_cmds = ""
        for x in range(len(fun_cmds_list)):
            fun_cmds += f"`{prefix}{fun_cmds_list[x].name}` "
        embed = discord.Embed(title="<:gigachad:845633149923753984> Giga Chad Help", color=0x2f3136,
                              description=f"`•` To see help on a category or on a commands do `{prefix}help Category` "
                                          f"or `{prefix}help command` (e.g `{prefix}help Fun` or `{prefix}help info`). "
                                          f"\n `•` The docs are available [here](https://docs.gigachad-bot.xyz)")
        embed.add_field(name="<:gc_emote:849913849158696960> Fun Commands",
                        value=f"`•` The fun commands are both normal command (that you call with the prefix `{prefix}` "
                              f"and [slash commands](https://support.discord.com/hc/fr/articles/1500000368501-Slash-Com"
                              f"mands-FAQ). If you can't see slash commands, type `{prefix}slash`for troubleshooting \n"
                              f"{fun_cmds}", inline=False)
        other_cog = self.context.bot.get_cog('Other')
        othr_cmds_list = other_cog.get_commands()
        othr_cmds = ""
        for x in range(len(othr_cmds_list)):
            othr_cmds += f"`{prefix}{othr_cmds_list[x].name}` "
        embed.add_field(name="<:settings:845659423561089034> Other Commands",
                        value=f"`•` These commands are all the other commands, mostly utility/information \n {othr_cmds}",
                        inline=False)
        embed.set_footer(text=f"Join the support server ({prefix}support) for further help")
        await self.context.reply(embed=embed, mention_author=False)

    async def send_command_help(self, command):
        prefix = get_prefix(self, self.context, True)
        embed = discord.Embed(title=f"`{prefix}{command.usage}`", color=0x2f3136,
                              description=f"\n `•` {command.description} \n `•` Category: {command.cog_name} \n *Argume"
                                          f"nts with [] aren't mandatory, while args with <> are*")
        embed.set_footer(text=f"Type {prefix}help for global help!")
        await self.context.reply(embed=embed, mention_author=False)

    async def send_cog_help(self, cog):
        prefix = get_prefix(self, self.context, True)
        cmds_list = cog.get_commands()
        cmds = ""
        for x in range(len(cmds_list)):
            cmds += f"`{prefix}{cmds_list[x].usage}` - {cmds_list[x].description} \n"
        cmds += "*Arguments with [] aren't mandatory, while args with <> are*"
        embed = discord.Embed(title=f"{cog.qualified_name} Category Help", color=0x2f3136, description=cmds)
        embed.set_footer(text=f"Type {prefix}help for global help!")
        await self.context.reply(embed=embed, mention_author=False)
