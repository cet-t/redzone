import asyncio
import random
from typing import Optional
import discord
from discord import app_commands
import json
import os
import datetime
from random import randint
# from ext import *


from data.member_data import *
from data.heist_data import *
from pyenv import channel_ids
from format2 import Format, Log

bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)


class GetPath:
    MEMBERS_DIR = '../members'
    LOG = '../log/cost.json'

    @staticmethod
    def members(id: int):
        return f'../members/{id}.json'

    @staticmethod
    def records(file_name: str):
        return f'../records/{file_name}.json'


@tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('pong')


@tree.command()
@app_commands.describe(count='count')
async def dice(interaction: discord.Interaction, count: int = 1):
    nums = ['one', 'two', 'three', 'four', 'five', 'six']
    result: list[str] = []
    for _ in range(count):
        result.append(f':{nums[randint(0, len(nums)-1)]}:')
    await interaction.response.send_message(str.join(' ', result))


@tree.command()
async def nkodice(interaction: discord.Interaction):
    pool = 'おちんこまう'
    result = ''
    for _ in range(len('おちんちん')):
        result += pool[randint(0, len(pool)-1)]
    await interaction.response.send_message(result)


@tree.command()
@app_commands.guild_only()
async def load_members(interaction: discord.Interaction):
    if len(files := os.listdir(GetPath.MEMBERS_DIR)) <= 0:
        return await interaction.response.send_message('0カモ…')
    members: list[str] = []
    for file in files:
        with open(f'../members/{file}', 'r') as f:
            member = MemberDict(json.load(f))
            members.append(f'<@{member["id"]}>: <@&{member["roles"][-1]}>')
    await interaction.response.send_message('\n'.join(members), ephemeral=True)


@tree.command()
async def disconnect(interaction: discord.Interaction):
    if interaction.user.id != 283584931437871104:
        return await interaction.response.send_message('権限がありません。', ephemeral=True)
    await interaction.response.send_message('10秒後にオフラインになります。', ephemeral=True)
    await asyncio.sleep(10)
    await asyncio.run(exit(0))


@tree.command()
@app_commands.describe(m_name='name', m_rank='rank', m_account='discord_account')
async def add_member(interaction: discord.Interaction, m_name: str, m_rank: RANK, m_account: discord.Member):
    try:
        data = MemberDict(
            name=m_name,
            rank=m_rank,
            id=m_account.id,
            roles=[role.id for role in m_account.roles if role.name != 'everyone']
        )
        if not os.path.exists(filepath := GetPath.members(m_account.id)):
            with open(filepath, 'x') as f:
                json.dump(data, f, indent=4)
            return await interaction.response.send_message(f'{m_account.mention}をメンバーに追加しました。')
        await interaction.response.send_message('rejected', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'rejected:{e}', ephemeral=True)


thread_id = None
now = datetime.datetime(2024, 4, 13, 1, 23)
htype = TYPE.FREECA
amounts: dict[int, int] = {}


@tree.command()
@app_commands.describe(type='type')
async def reward(interaction: discord.Interaction, type: TYPE):
    global thread_id, now, htype
    htype = type
    now = datetime.datetime.now()
    def zf(item: int) -> str: return str(item).zfill(2)
    title = f'{type.name}_{zf(now.year)}{zf(now.month)}{zf(now.day)}{zf(now.hour)}{zf(now.minute)}'
    channel = interaction.channel
    thread: discord.Thread = await channel.create_thread(name=title, type=discord.ChannelType.public_thread)  # type: ignore
    thread_id = thread.id
    await interaction.response.send_message(f'{thread.mention}: 作成しました。')
    rand = randint(2**5, 2**10)
    info = f'入手額が{rand}万円の場合は、{rand}と入力してください。\n\n'
    info += '`!calc`: 入力された値の合計値を計算します。\n'
    info += '`!del`: 入力された値を削除します。(入力した本人のみ削除可能)'
    await thread.send(info)


@tree.command()
@app_commands.describe(member='member')
async def stats(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    if len(record_files := os.listdir('../records')) <= 0:
        await interaction.response.send_message('記録がありません。', ephemeral=True)
    data: list[HeistRecordDict] = []
    if member is not None:
        for record in record_files:
            with open(record, 'r') as f:
                data.append(HeistRecordDict(json.load(f)))
        pass
    else:
        pass
    print(data)


@tree.command(name='cost', description='経費精算, チームプール管理')
@app_commands.describe(amount='金額', note='備考')
async def cost_production(interaction: discord.Interaction, amount: int, note: Optional[str] = None):
    if interaction.channel_id != channel_ids['redzone']:
        return await interaction.response.send_message(f'<#{channel_id}>専用チャンネルで使用してください。', ephemeral=True)
    if not os.path.exists(file_path := '../log/cost.json'):
        return await interaction.response.send_message(f'ログファイルが存在しません。', ephemeral=True)
    try:    
        with open(GetPath.LOG, 'r', encoding='utf_8_sig') as f:
            load_data = Format(json.load(f, strict=False))
            pool, logs = load_data['pool'] + amount, load_data['logs']
            now = datetime.datetime.now()
            log = Log(
                datetime=f'{now.year}{now.month}{now.day}{now.hour}',
                user_id=interaction.user.id,
                amount=amount,
                note=note
            )
            logs.append(log)
            load_data = Format(pool=pool, logs=logs)
            with open(GetPath.LOG, 'w') as ff:
                json.dump(load_data, ff, indent=4)
                message = f'{interaction.user.mention}'+ '\n' + f'金額: {format(amount, ",")}'+'\n'+f'備考:{note}'+'\n'+f'チームプール: {format(pool, ",")}'
                colour = discord.Colour.blue() if amount > 0 else discord.Colour.brand_red()
        await interaction.response.send_message(embed=discord.Embed(title='経費精算・チームプール管理', description=message, colour=colour))
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)


@bot.event
async def on_message(message: discord.Message):
    global thread_id
    if message.author.bot or thread_id is None:
        return
    print('thread id:', thread_id)

    if message.content == '!data' and len(amounts) > 0:
        return await message.reply('\n'.join([f'<@{m}>: {a}' for m, a in amounts.items()]))
    elif message.content == '!calc':
        if len(amounts) <= 0:
            return await message.reply('値が入力されていません。')
        total = len(amounts.values())
        member_count = len(amounts)
        dst = f'合計金額: {sum(amounts.values())}万円\n'
        dst += f'参加者数: {member_count}\n'
        dst += f'1人{total/member_count}万円({total}/{member_count})\n'
        try:
            record_data = HeistRecordDict(
                date=now.strftime('%Y%m%d%H%M%S'),
                members_reward=amounts,
                total_amount=total
            )
            with open(GetPath.records(f'{htype.name}_{record_data["date"]}'), 'x') as f:
                json.dump(record_data, f, indent=4)
        except:
            pass
        await message.channel.send(dst)
        amounts.clear()
        thread_id = None
        return
    if message.content.startswith('!del'):
        try:
            user_id = message.author.id
            for id, _ in amounts.items():
                if id == user_id:
                    del amounts[user_id]
                    # amounts.__delitem__(id)
                    return await message.reply('削除しました。')
        except RuntimeError:
            # 捻じ伏せる
            pass
    if message.channel.id == thread_id:
        try:
            amounts[message.author.id] = int(message.content)
        except Exception as e:
            pass
            # await message.channel.send(f'{message.author.mention}:{str(e)}')
    else:
        await message.reply('murikamo...T_T')
    print(amounts)


if __name__ == '__main__':
    @bot.event
    async def on_ready():
        await tree.sync()
        await bot.change_presence(
            activity=discord.Streaming(
                name='CCGTA',
                url='https://twitch.tv/example'),
            status=discord.Status.do_not_disturb
        )
        print('ok.')

    from core import Core
    bot_core = Core('TOKEN')
    if bot_core.load_environ():
        bot.run(bot_core.token)
    else:
        exit(-1)
