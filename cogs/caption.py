import discord
import os
import asyncio
import traceback
from discord.ext import commands
from cogs.fun import error_api


class Caption(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad

    @cog_ext.cog_slash(name="caption",
                       description="🎭 Caption a meme, 25 meme templates available!",
                       options=[
                           create_option(
                               name="template",
                               description="Choose a meme template",
                               option_type=3,
                               required=True,
                               choices=[
                                   create_choice(name="Two Buttons", value="87743020"),
                                   create_choice(name="Distracted Boyfriend", value="112126428"),
                                   create_choice(name="Drake Yikes", value="181913649"),
                                   create_choice(name="Batman Slaps Robin", value="438680"),
                                   create_choice(name="Trade Offer", value="309868304"),
                                   create_choice(name="Change my Mind", value="129242436"),
                                   create_choice(name="UNO Draw 25", value="217743513"),
                                   create_choice(name="Woman Yelling at Cat", value="188390779"),
                                   create_choice(name="Inhaling Seagull", value="114585149"),
                                   create_choice(name="Giga Chad", value="190327839"),
                                   create_choice(name="Another Woman", value="110163934"),
                                   create_choice(name="Same Pictures", value="180190441"),
                               ]
                           ),
                           create_option(
                               name="top_caption",
                               description="Write the top text",
                               option_type=3,
                               required=True
                           ),
                           create_option(
                               name="bottom_caption",
                               description="Write the bottom text",
                               option_type=3,
                               required=True
                           ),
                       ])
    async def caption(self, ctx: SlashContext, template: int, top_caption: str, bottom_caption: str):
        try:
            pload = {'font': 'impact', 'username': 'Thorgal108', 'password': 'zrRyU&D!FxpK3T3',
                     'template_id': template, 'text1': bottom_caption, 'text0': top_caption}
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.imgflip.com/caption_image', data=pload) as r:
                    data = await r.read()
            json_data = json.loads(data)
            embed = discord.Embed(color=0x2f3136)
            embed.set_image(url=json_data['data']['url'])
            embed.set_author(name='Click to access the post', url=json_data['data']['page_url'])
            embed.set_footer(text="Made with the imgflip.com API")
            await ctx.send(embed=embed, hidden=False)

        except:
            await error_api(ctx)


def setup(gigachad):
    gigachad.add_cog(Caption(gigachad))
