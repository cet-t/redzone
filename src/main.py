﻿import asyncio
import discord
from discord import app_commands
import json
import os
import datetime
import random

from traitlets import default

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
htype = HEIST_TYPE.FREECA
amounts: dict[int, int] = {}


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
    thread: discord.Thread = await ch.create_thread(  # type: ignore
        name=title,
        type=discord.ChannelType.public_thread  # type: ignore
    )
    thread_id = thread.id
    # print(f'is private: {thread.is_private()}')
    await interaction.response.send_message(f'{thread.mention}: 作成しました。')
    rand = random.randint(2**5, 2**10)
    await thread.send(f'入手額{rand}万円の場合{rand}と入力してください。')
    await thread.send('全員が入力し終わったら`!calc`を送信してください。')


@tree.command()
async def modaltest(interaction: discord.Interaction):
    modal = discord.ui.Modal(title='test')
    modal.add_item(item=discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label='test button',
    ))
    await interaction.response.send_modal(modal)


@bot.event
async def on_message(message: discord.Message):
    global thread_id
    if message.author.bot or thread_id is None:
        return
    print('thread id:', thread_id)

    match message.content:
        case '!calc':
            if len(amounts) <= 0:
                return await message.reply('値が入力されていません。')
            total = 0
            for _, amount in amounts.items():
                total += amount
            member_count = 0
            for member in message.guild.members:  # type: ignore
                if not member.bot:
                    member_count += 1
            dst = f'合計金額: {sum(amounts.values())}万円\n'
            dst += f'メンバー数: {member_count}\n'
            dst += f'1人{total/member_count}万円({total}/{member_count})\n'
            try:
                record_data = HeistRecordDict(
                    date=now.strftime('%Y%m%d%H%M%S'),
                    members_reward=amounts,
                    total_amount=total
                )
                with open(GetPath.records(f'{htype.name}_{record_data['date']}'), 'x') as f:
                    json.dump(record_data, f, indent=4)
            except:
                pass
            await message.channel.send(dst)
            amounts.clear()
            thread_id = None
            # return

    if message.channel.id == thread_id:
        try:
            amounts[message.author.id] = int(message.content)
        except Exception as e:
            await message.channel.send(f'{message.author.mention}:{str(e)}')
    print(amounts)


if __name__ == '__main__':
    @bot.event
    async def on_ready():
        print('ok.')
        await tree.sync()
        await bot.change_presence(
            activity=discord.Streaming(
                name='CCGTA',
                url='https://twitch.tv/example'),
            status=discord.Status.do_not_disturb
        )

    from core import Core
    bot_core = Core('TOKEN')
    if bot_core.load_environ():
        bot.run(bot_core.token)
    else:
        exit(-1)
