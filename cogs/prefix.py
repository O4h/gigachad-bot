import discord
import asyncio
import json
from discord.ext import commands


def get_prefix(bot, message):
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
            return commands.when_mentioned_or(prefixes[str(message.guild.id)])(bot, message)

    except KeyError:
        with open('prefixes.json', 'r') as k:
            prefixes = json.load(k)
        prefixes[str(message.guild.id)] = 'gc!'

        with open('prefixes.json', 'w') as j:
            json.dump(prefixes, j, indent=4)

        with open('prefixes.json', 'r') as t:
            prefixes = json.load(t)
            return commands.when_mentioned_or(prefixes[str(message.guild.id)])(bot, message)

    except:
        return commands.when_mentioned_or("gc!")(bot, message)


def get_prefix_raw(message):
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
            return prefixes[str(message.guild.id)]
            print('was found')

    except KeyError:
        print('was not found')
        with open('prefixes.json', 'r') as k:
            prefixes = json.load(k)
        prefixes[str(message.guild.id)] = 'gc!'

        with open('prefixes.json', 'w') as j:
            json.dump(prefixes, j, indent=4)

        with open('prefixes.json', 'r') as t:
            prefixes = json.load(t)
            return prefixes[str(message.guild.id)]

    except:
        print('was in dm')
        return "gc!"


class Prefix(commands.Cog):
    def __init__(self, gigachad):
        self.gigachad = gigachad


def setup(gigachad):
    gigachad.add_cog(Prefix(gigachad))
