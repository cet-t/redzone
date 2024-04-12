﻿import asyncio
import discord
from discord import app_commands
import json
import os
from datetime import datetime, tzinfo
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

    @staticmethod
    def records(file_name: str):
        return f'../records/{file_name}.json'


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
    await interaction.response.send_message('10秒後にオフラインになります。', ephemeral=True)
    await asyncio.sleep(10)
    exit(0)


# @tree.command()
# async def add_rob_record(interaction: discord.Interaction):
#     pass


@tree.command()
@app_commands.describe(m_name='name', m_rank='rank', m_account='discord_account')
async def add_member(interaction: discord.Interaction, m_name: str, m_rank: RANK, m_account: discord.Member):
    member_data = MemberDict(
        name=m_name,
        rank=m_rank,
        id=m_account.id,
        roles=[role.id for role in m_account.roles]
    )
    try:
        if not os.path.exists(filepath := GetPath.members(m_account.id)):
            with open(filepath, 'x') as f:
                json.dump(member_data, f, indent=4)
            return await interaction.response.send_message(f'{m_account.mention}をメンバーに追加しました。')
        await interaction.response.send_message('rejected', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'rejected:{e}', ephemeral=True)


thread_id = None
now = datetime.datetime(2024, 4, 13, 1, 23)
htype = HEIST_TYPE.FREECA


@tree.command()
@app_commands.describe(type='type')
async def reward(interaction: discord.Interaction, type: HEIST_TYPE):
    global thread_id, now, htype
    htype = type
    now = datetime.datetime.now()
    def f(item: int) -> str: return str(item).zfill(2)
    title = f'{type.name}{f(now.year)}{f(now.month)}{f(now.day)}{
        f(now.hour)}{f(now.minute)}'
    ch = interaction.channel
    # print('ch:', ch.id)  # type: ignore
    thread: discord.Thread = await ch.create_thread(name=title)  # type: ignore
    thread_id = thread.id
    thread_url = f'https://discord.com/channels/{
        interaction.guild_id}/{thread_id}'
    # await interaction.response.send_message(f'{thread.mention}: 作成しました。')
    await interaction.response.send_message(f'{thread.mention}||{thread_url[1:]}||')
    rand = random.randint(2**5, 2**10)
    await thread.send(f'入手額{rand}万円の場合{rand}と入力してください。')

# ID, AMOUNT = 0, 1
# amounts: list[tuple[int, int]] = []  # amounts[index](ID, AMOUNT)
amounts2: dict[int, int] = {}


@bot.event
async def on_message(message: discord.Message):
    global thread_id
    if message.author.bot or thread_id is None:
        return
    print('thread id:', thread_id)

    # if len(amounts) > 0 and message.content == '!calc':
    if len(amounts2) > 0 and message.content == '!calc':
        total = 0
        # for amount in amounts:
        for _, amount in amounts2.items():
            total += amount
        # text_list = [f'合計金額:{str(total)}万円\n']
        text_list = f'合計金額:{sum(amounts2.values())}万円\n'
        member_count = 0
        for member in message.guild.members:  # type: ignore
            if not member.bot:
                member_count += 1
        text_list += f'メンバー数: {member_count}\n'
        text_list += f'1人{total//member_count}万円({total}/{member_count}) ※切捨\n'
        # amounts.clear()
        try:
            record_data = HeistRecordDict(
                date=now.strftime('%Y%m%d%H%M%S'),
                members_reward=amounts2,
                total_amount=total
            )
            with open(GetPath.records(f'{htype.name}_{record_data['date']}'), 'x') as f:
                json.dump(record_data, f, indent=4)
        except:
            pass
        await message.channel.send(text_list)
        amounts2.clear()
        # message.guild.get_thread(thread_id).archived = True  # type: ignore
        thread_id = None
        return

    if thread_id is not None and message.channel.id == thread_id:
        # if len(amounts) > 0:
        # for amount in amounts:
        # if len(amounts2) > 0:
        #     for _, amount in amounts2.items():
        #         if amount == message.author.id:
        #             return await message.channel.send(f'{message.author.mention}: already registerd')

        try:
            # amounts.append((message.author.id, int(message.content)))
            amounts2[message.author.id] = int(message.content)
        except Exception as e:
            await message.channel.send(f'{message.author.mention}:{str(e)}')
    print(amounts2)


@ bot.event
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

    @ bot.event
    async def on_ready():
        print('ok.')
        await tree.sync()

    bot.run(token)
