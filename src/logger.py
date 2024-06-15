import discord


def error(issue: str):
    return f'[ERROR] {issue}'


def code_block(text: str):
    return f'`{text}`'


def error_embed(description: str):
    embed = discord.Embed(
        title='Raise exception',
        description=description,
        colour=discord.Colour.red()
    )
    embed.set_footer(text='🔥REDZONE🔥')
    return embed


def warn_embed(description: str):
    embed = discord.Embed(
        title='Warning',
        description=description,
        colour=discord.Colour.pink()
    )
    embed.set_footer(text='🔥REDZONE🔥')
    return embed
