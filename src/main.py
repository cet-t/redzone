import discord
from discord import app_commands
import json
import os

from data.member_data import *

bot = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(bot)


@tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('hello')


@tree.command()
@app_commands.guild_only()
async def load_members(interaction: discord.Interaction):
    if len(files := os.listdir('../members_db')) <= 0:
        return await interaction.response.send_message('0カモ…')
    text = ''
    for file in files:
        with open(f'../members_db/{file}', 'r') as f:
            member = MemberDict(json.load(f))
            # text += f'<@{member["id"]}>{RANK.to_rank(member['rank'])}\n'
            text += f'<@{member['id']}><@&{member['roles'][-1]}>\n'
    await interaction.response.send_message(text, ephemeral=True)


@tree.command()
@app_commands.describe(m_name='name', m_rank='rank', m_account='discord_account')
async def add_member(interaction: discord.Interaction, m_name: str, m_rank: RANK, m_account: discord.Member):
    member_data = MemberDict(
        name=m_name,
        rank=m_rank,
        id=m_account.id,
        roles=[role.id for role in m_account.roles]
    )
    if not os.path.exists(filepath := f'../members_db/{m_account.id}.json'):
        with open(filepath, 'x') as f:
            json.dump(member_data, f, indent=4)
        return await interaction.response.send_message(f'{m_account.mention}をメンバーに追加しました。ようこそ！')
    await interaction.response.send_message('失敗しちゃった…もうメンバーかも…？', ephemeral=True)

if __name__ == '__main__':
    try:
        import pyenv
        token = pyenv.TOKEN
    except KeyError:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.environ['TOKEN']

    @bot.event
    async def on_ready():
        await tree.sync()
        print('ok.')

    bot.run(token)
