from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
import os
import random
import discord
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import urllib.request

load_dotenv()

default_intents = discord.Intents.default()
intents = discord.Intents(messages=True)


class GigaChad(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="gc!", intents=intents)

    async def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print(discord.__version__)
        print('------')


gigachad = GigaChad()
gigachad.remove_command('help')

slash = SlashCommand(gigachad, sync_commands=True)

guild_ids = [844911117881180190]


@slash.slash(name="caption",
             description="🎭 Caption a meme, 25 meme templates available!",  guild_ids=guild_ids,
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
async def caption(ctx, template: int, top_caption: str, bottom_caption: str):
    pload = {'font': 'impact', 'username': 'Thorgal108', 'password': 'zrRyU&D!FxpK3T3', 'template_id': template,
             'text1': bottom_caption, 'text0': top_caption}
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


@slash.slash(name="Meme", description='🎲 Get a random meme!',  guild_ids=guild_ids,
             options=[
                 create_option(
                     name="subreddit",
                     description="Get a meme from a particular subreddit",
                     option_type=3,
                     required=False,
                 )])
async def meme(ctx, subreddit='default'):
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


@slash.slash(name="chadmeter", description="📏 Scientifically measure your Chad level", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="Check the chad lever of another user",
                     option_type=6,
                     required=False,
                 )])
async def chadmeter(ctx, user: discord.user = True):
    chadlevel = random.randint(0, 100)
    if ctx.author.id == 541940250428047370:
        if user:
            chadlevel = 100

    if user:
        message = f'Your Chad level is {chadlevel}%!'
    else:
        if user.id == 541940250428047370 or 843550872293867570:
            chadlevel = 100
        message = f"{user.mention}'s Chad level is `{chadlevel}%`!"
    embed = discord.Embed(title="📏 Chadmeter", description=message, color=0x2f3136)
    embed.set_footer(icon_url=gigachad.user.avatar_url, text="Chadmeter never lies, Copyrighted © method")
    embed.set_thumbnail(
        url="https://preview.redd.it/23td86ox29j51.png?auto=webp&s=c617e39e98b1e601cc91168369bd6ea38cd55f89")
    await ctx.send(embed=embed, hidden=False)


@slash.slash(name="gigachadify", description="💫 Gigadify yourself or another user!", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="GigaChadify another user!",
                     option_type=6,
                     required=False,
                 )])
async def gigachadify(ctx, user: discord.user = True):
    if user == True:
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
    if user != True:
        if user.id == gigachad.user.id:
            prefix = "I am Giga Chad. I gigachadify, I can't be gigachidified."
            footer = "Yep. That's me"
            file = discord.File("gigachad.png")
            attachment = "attachment://gigachad.png"
    embed = discord.Embed(title=prefix, color=0x2f3136)
    embed.set_footer(icon_url=gigachad.user.avatar_url, text=footer)
    embed.set_image(url=attachment)
    await ctx.send(file=file, embed=embed)


@gigachad.command()
async def help(ctx):
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


@gigachad.command(aliases=['about'])
async def info(ctx):
    embed = discord.Embed(title="<:gigachad:843818002616418367> Giga Chad Info", color=0x2f3136,
                          description="Giga Chad is a bot written in Python <:python:844904483946364935> by "
                                      "`Thorgal#0982` using the discord.py and discord-py-slash-command librairies.")
    embed.add_field(name="Credits", value="`•` The GigaChadBot profile picture and images are from [@berlin.1969]"
                                          "(https://www.instagram.com/berlin.1969/)'s instagram.", inline=False)
    embed.add_field(name="APIs", value="`•` [imgflip.com](https://imgflip.com/)'s API \n `•` [reddit.com]("
                                       "https://www.reddit.com/)'s API", inline=False)
    embed.set_footer(text="DM Thorgal#0982 for further information")
    await ctx.send(embed=embed)


@gigachad.command()
async def invite(ctx):
    embed = discord.Embed(title="Invite Giga Chad!", color=0x2f3136,
                          description="Click [here](https://discord.com/api/oauth2/authorize?client_id"
                                      "=843550872293867570&permissions=2147551232&scope=bot%20applications.commands) "
                                      "to invite Giga Chad!")
    await ctx.send(embed=embed)


gigachad.run(os.getenv("TOKEN"))
