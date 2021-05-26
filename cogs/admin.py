import discord
import os
import asyncio
import traceback
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if cog is None:
            embed = discord.Embed(title="<:settings:845659423561089034> Reloading all cogs.", color=0x2f3136,)
            for ext in os.listdir("./cogs/"):
                if ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.gigachad.unload_extension(f"cogs.{ext[:-3]}")
                        self.gigachad.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(name=f"Reloaded: `{ext}`", value='\uFEFF', inline=False)
                    except Exception as e:
                        embed.add_field(name=f"Failed to reload: `{ext}`", value=e, inline=False)
                    await asyncio.sleep(0.5)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"<:settings:845659423561089034> Reloading cog `{cog}.py`", color=0x2f3136)
            ext = f"{cog.lower()}.py"
            if not os.path.exists(f"./cogs/{ext}"):
                embed.add_field(name=f"Failed to reload: `{ext}`", value="This cog does not exist.", inline=False)
            elif ext.endswith(".py") and not ext.startswith("_"):
                try:
                    self.gigachad.unload_extension(f"cogs.{ext[:-3]}")
                    self.gigachad.load_extension(f"cogs.{ext[:-3]}")
                    embed.add_field(name=f"Reloaded: `{ext}`", value='\uFEFF', inline=False)
                except Exception:
                    desired_trace = traceback.format_exc()
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`", value=desired_trace, inline=False)
            await ctx.send(embed=embed)


def setup(gigachad):
    gigachad.add_cog(Admin(gigachad))
