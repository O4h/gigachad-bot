import random
import discord
import requests
import urllib.request
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from io import BytesIO
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

load_dotenv()

IMGFLIP_USERNAME = os.getenv("IMGLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")


class Fun(commands.Cog):
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
                                   create_choice(
                                       name="Two Buttons",
                                       value="87743020"
                                   ),
                                   create_choice(
                                       name="Distracted Boyfriend",
                                       value="112126428"
                                   ),
                                   create_choice(
                                       name="Drake Yikes",
                                       value="181913649"
                                   ),
                                   create_choice(
                                       name="Batman Slaps Robin",
                                       value="438680"
                                   ),
                                   create_choice(
                                       name="Trade Offer",
                                       value="309868304"
                                   ),
                                   create_choice(
                                       name="Change my Mind",
                                       value="129242436"
                                   ),
                                   create_choice(
                                       name="UNO Draw 25",
                                       value="217743513"
                                   ),
                                   create_choice(
                                       name="Woman Yelling at Cat",
                                       value="188390779"
                                   ),
                                   create_choice(
                                       name="Inhaling Seagull",
                                       value="114585149"
                                   ),
                                   create_choice(
                                       name="Giga Chad",
                                       value="190327839"
                                   ),
                                   create_choice(
                                       name="Another Woman",
                                       value="110163934"
                                   ),
                                   create_choice(
                                       name="Same Pictures",
                                       value="180190441"
                                   ),
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
        pload = {'font': 'impact', 'username': IMGFLIP_USERNAME, 'password': IMGFLIP_PASSWORD,
                 'template_id': template, 'text1': bottom_caption, 'text0': top_caption}
        r = requests.post('https://api.imgflip.com/caption_image', data=pload)
        r_dictionary = r.json()
        data = r_dictionary['data']
        url = data['url']
        page_url = data['page_url']
        embed = discord.Embed(color=0x2f3136)
        embed.set_image(url=url)
        embed.set_author(name='Click to access the post', url=page_url)
        embed.set_footer(text="Made with the imgflip.com API")
        await ctx.send(embed=embed, hidden=False)

    @cog_ext.cog_slash(name="Meme", description='🎲 Get a random meme!',
                       options=[
                           create_option(
                               name="subreddit",
                               description="Get a meme from a particular subreddit",
                               option_type=3,
                               required=False,
                           )])
    async def meme(self, ctx: SlashContext, subreddit='default'):
        if subreddit == 'default':
            r = requests.get('https://meme-api.herokuapp.com/gimme')
        else:
            r = requests.get(f'https://meme-api.herokuapp.com/gimme/{subreddit}')
        r_dictionnary = r.json()
        nsfw = r_dictionnary['nsfw']
        if nsfw:
            await ctx.send(content="Sorry, the meme was NSFW. Try another one!", hidden=True)
            return
        link = r_dictionnary['postLink']
        title = r_dictionnary['title']
        subreddit = r_dictionnary['subreddit']
        author = r_dictionnary['author']
        image = r_dictionnary['url']
        embed = discord.Embed(color=0x2f3136, url=link, title=title)
        embed.set_footer(text=f'r/{subreddit} | u/{author}')
        embed.set_image(url=image)
        await ctx.send(embed=embed, hidden=False)

    @cog_ext.cog_slash(name="chadmeter", description="📏 Scientifically measure your Chad level",
                       options=[
                           create_option(
                               name="user",
                               description="Check the chad lever of another user",
                               option_type=6,
                               required=False,
                           )])
    async def chadmeter(self, ctx: SlashContext, user: discord.user = True):
        chadlevel = random.randint(0, 100)
        if ctx.author.id == 541940250428047370:
            if user:
                chadlevel = 100

        if user:
            message = f'Your Chad level is {chadlevel}%!'
        else:
            appinfo = await self.gigachad.application_info()
            if user.id == appinfo.owner.id or self.gigachad.user.id:
                chadlevel = 100
            message = f"{user.mention}'s Chad level is `{chadlevel}%`!"
        embed = discord.Embed(title="📏 Chadmeter", description=message, color=0x2f3136)
        embed.set_footer(icon_url=self.gigachad.user.avatar_url, text="Chadmeter never lies, Copyrighted © method")
        embed.set_thumbnail(
            url="https://preview.redd.it/23td86ox29j51.png?auto=webp&s=c617e39e98b1e601cc91168369bd6ea38cd55f89")
        await ctx.send(embed=embed, hidden=False)

    @cog_ext.cog_slash(name="gigachadify", description="💫 Gigadify yourself or another user!",
                       options=[
                           create_option(
                               name="user",
                               description="GigaChadify another user!",
                               option_type=6,
                               required=False,
                           )])
    async def gigachadify(self, ctx: SlashContext, user: discord.user = True):
        if user is True:
            asset = ctx.author.avatar_url_as(size=128)
            prefix = "You look gorgeous, surely not as good as I do, but still..."
        else:
            asset = user.avatar_url_as(size=128)
            prefix = "They look gorgeous, surely not as good as I do, but still..."
        urllib.request.urlretrieve('https://i.imgur.com/gZJihTV.png', "gigachad.png")
        im1 = Image.open("gigachad.png")
        data = BytesIO(await asset.read())
        im2 = Image.open(data)
        im2 = im2.resize((175, 175))
        mask_im = Image.new("L", im2.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse([(0, 0), (175, 175)], fill=255)
        mask_im.save('mask_circle.jpg', quality=95)
        im2 = im2.rotate(7)
        im1.paste(im2, (300, 85), mask_im)
        im1.save("test.jpg", quality=95)
        footer = "Feel free to use this picture of yourself in your resume, or on any dating site"
        file = discord.File("test.jpg")
        attachment = "attachment://test.jpg"
        if user is not True:
            if user.id == self.gigachad.user.id:
                prefix = "I am Giga Chad. I gigachadify, I can't be gigachidified."
                footer = "Yep. That's me"
                file = discord.File("gigachad.png")
                attachment = "attachment://gigachad.png"
        embed = discord.Embed(title=prefix, color=0x2f3136)
        embed.set_footer(icon_url=self.gigachad.user.avatar_url, text=footer)
        embed.set_image(url=attachment)
        await ctx.send(file=file, embed=embed)

    @cog_ext.cog_slash(name="quote", description="💬 Get an inspiring quote to get closer to being a Giga Chad")
    async def quote(self, ctx: SlashContext):
        r = requests.get('https://api.fisenko.net/quotes')
        r_dictionnary = r.json()
        quote = r_dictionnary['text']
        author = r_dictionnary['author']
        embed = discord.Embed(title="💬 Inspiring quote", color=0x2f3136,
                              description=f"<:quote1:845745030912278598> \n**{quote}** \n <:blank:845752143226077245>"
                                          "<:blank:845752143226077245><:blank:845752143226077245> "
                                          "<:blank:845752143226077245> "
                                          "<:blank:845752143226077245><:blank:845752143226077245> "
                                          f"<:blank:845752143226077245><:quote2:845745030978994216> \n - {author}")
        embed.set_footer(text="I hope this quote inspired you to become a Giga Chad")
        await ctx.send(embed=embed, hidden=False)

    @cog_ext.cog_slash(name="advice", description="💡 Get some advice from Giga Chad")
    async def quote(self, ctx: SlashContext):
        r = requests.get('https://api.adviceslip.com/advice')
        r_dictionnary = r.json()
        advice_id = r_dictionnary['id']
        advice = advice_id['advice']
        embed = discord.Embed(title="💡 Helpful Advice", color=0x2f3136,
                              description=f"🗣 {advice}")
        embed.set_footer(text="Follow or not this advice, up to you")
        await ctx.send(embed=embed, hidden=False)


def setup(bot):
    bot.add_cog(Fun(bot))
