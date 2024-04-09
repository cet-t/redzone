import discord
from discord import app_commands
import json
import os
import datetime
import random

from data.member_data import *
from data.heist_data import *
from admins import *

bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)


class GetPath:
    MEMBERS_DIR = '../members'

    @staticmethod
    def members(id: int):
        return f'../members/{id}.json'


@tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('hello')


@tree.command()
@app_commands.guild_only()
async def load_members(interaction: discord.Interaction):
    if len(files := os.listdir(GetPath.MEMBERS_DIR)) <= 0:
        return await interaction.response.send_message('0カモ…')
    members: list[str] = []
    for file in files:
        with open(f'../members/{file}', 'r') as f:
            member = MemberDict(json.load(f))
            members.append(f'<@{member['id']}>: <@&{member['roles'][-1]}>')
    await interaction.response.send_message('\n'.join(members), ephemeral=True)


@tree.command()
async def disconnect(interaction: discord.Interaction):
    if interaction.user.id != admins[0]:
        return await interaction.response.send_message('権限がありません。', ephemeral=True)
    return await interaction.response.send_message('権限がありません。', ephemeral=True)


@tree.command()
async def add_rub_record(interaction: discord.Interaction):
    pass


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
        return await interaction.response.send_message(f'{m_account.mention}をメンバーに追加しました。')
    await interaction.response.send_message('rejected', ephemeral=True)


thread_id = None


@tree.command()
@app_commands.describe(type='heist type')
async def reward_calc(interaction: discord.Interaction, type: HEIST_TYPE):
    global thread_id
    ch = interaction.channel
    now = datetime.datetime.now().date()
    title = f'{type.name}{str(now.year).zfill(2)}{str(
        now.month).zfill(2)}{str(now.day).zfill(2)}'
    thread: discord.Thread = await ch.create_thread(name=title)  # type: ignore
    thread_id = thread.id
    await interaction.response.send_message(f'{thread.mention}:作成しました。')
    rand = random.randint(1, 512)
    await thread.send(f'入手額{rand}万円の場合{rand}と入力してください。')


ID, AMOUNT = 0, 1
amounts: list[tuple[int, int]] = []  # amounts[index](ID, AMOUNT)


@bot.event
async def on_message(message: discord.Message):
    global thread_id
    if message.author.bot:
        return
    print('thread id:', thread_id)

    if len(amounts) > 0 and message.content == '!calc':
        total = 0
        for amount in amounts:
            total += amount[AMOUNT]
        # message.guild.get_thread(thread_id).   # type: ignore
        thread_id = None
        text = f'合計金額:{str(total)}万円\n'
        member_count = 0
        for member in message.guild.members:  # type: ignore
            if not member.bot:
                member_count += 1
        text += f'メンバー数: {member_count}\n'
        text += f'1人{total/member_count}万円({total}/{member_count})\n'
        amounts.clear()
        return await message.channel.send(text)

    if thread_id != None or message.channel.id == thread_id:
        if len(amounts) > 0:
            for amount in amounts:
                if amount[ID] == message.author.id:
                    return await message.channel.send(f'{message.author.mention}: already registerd')

        try:
            amounts.append((message.author.id, int(message.content)))
        except Exception as e:
            await message.channel.send(f'{message.author.mention}:{str(e)}')
        print(amounts)


@bot.event
async def on_():
    pass

if __name__ == '__main__':
    # for heist in heists:
    # with open(f'../heists/{str(heist['name'].name).lower()}.json', 'x') as f:
    # json.dump(heist, f, indent=4)

    try:
        import pyenv
        token = pyenv.TOKEN
    except KeyError:
        import dotenv
        dotenv.load_dotenv()
        token = os.environ['TOKEN']

    @bot.event
    async def on_ready():
        print('ok.')
        await tree.sync()

    bot.run(token)
