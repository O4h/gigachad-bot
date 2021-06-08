import json


def get_emote(emote: str):
    """ Return an emote from emotes.json"""
    with open('util/emotes.json', 'r') as f:
        emotes = json.load(f)

    if str(emote) in emotes:
        return emotes[str(emote)]

    else:
        return ":exclamation:"


def get_category_emote(category: str):
    """ Return a category-related emote"""
    return
