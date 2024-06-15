import discord


def error(issue: str):
    return f'[ERROR] {issue}'


def code_block(text: str):
    return f'`{text}`'


def error_embed(title: str, description: str):
    return discord.Embed(title=title, description=description)
