import asyncio
from collections import UserDict
from typing import Optional
import discord
from discord import app_commands
import json
import os
from datetime import datetime
from random import randint


from data.member_data import *
from data.heist_data import *
from pyenv import channel_ids, file_path, user_ids
from format2 import LogDict, LogDataDict, LogDataKey, LogKey
import utility

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
async def disconnect(interaction: discord.Interaction):
    if interaction.user.id != 283584931437871104:
        return await interaction.response.send_message('権限がありません。', ephemeral=True)
    await interaction.response.send_message('10秒後にオフラインになります。', ephemeral=True)
    await asyncio.sleep(10)
    await asyncio.run(exit(0))


@tree.command(name='cost', description='経費精算, チームプール管理')
@app_commands.describe(amount='金額', note='支払内容')
async def cost_production(interaction: discord.Interaction, amount: int, note: Optional[str] = None):
    # 専用チャンネル外で使用
    if not interaction.channel_id in channel_ids.values():
        return await interaction.response.send_message(embed=utility.warn_embed(f'<#{channel_ids.get("redzone")}>で使用してください。'), ephemeral=True)
    # ファイルが存在しない
    if not os.path.exists(file_path):
        return await interaction.response.send_message(embed=utility.error_embed(f'ログファイルが存在しません。'), ephemeral=True)

    with open(file_path, 'r') as f:
        if (load_data := LogDict(json.load(f))) is None:
            return await interaction.response.send_message('ファイルを読み込めませんでした。', ephemeral=True)

        pool, logs = load_data.get(LogKey.POOL), load_data.get(LogKey.LOGS)

        is_boss = interaction.user.id == user_ids.get('boss')

        # ボス
        if interaction.user.id == user_ids.get('boss'):
            pool += amount
        log = LogDataDict(
            id=len(logs),
            datetime=datetime.now().isoformat(),
            user_id=interaction.user.id,
            amount=amount,
            note=note,
            is_cancelled=False,
            is_pending=not is_boss
        )
        logs.append(log)
        load_data = LogDict(pool=pool, logs=logs)
        with open(file_path, 'w') as ff:
            json.dump(load_data, ff, indent=4)
            emb = discord.Embed(
                title=utility.inline_code_block(f'#{log.get("id")}')+' 精算',
                description='',
                color=discord.Color.blue() if amount >= 0 else discord.Color.brand_red()
            )
            emb.add_field(name='金額', value=utility.code_block(format(amount, ',')), inline=False)
            if note != None:
                emb.add_field(name='支払内容', value=utility.code_block(note), inline=False)
            emb.add_field(name='チームプール', value=utility.code_block(format(pool, ',')), inline=False)
            emb.set_footer(text='🔥REDZONE🔥')
            await interaction.response.send_message(embed=emb)


def exists_log(logs: list[LogDataDict], log_id: int) -> bool:
    for log in logs:
        if log.get(LogDataKey.ID) == log_id:
            return True
    return False


@tree.command(name='cancel', description='取消')
@app_commands.describe(id='log_id')
async def cost_cancel(interaction: discord.Interaction, id: int):
    if not interaction.channel_id in channel_ids.values():
        return await interaction.response.send_message(embed=utility.warn_embed(f'<#{channel_ids.get("redzone")}>で使用してください。'), ephemeral=True)

    with open(file_path, 'r') as f:
        # ログファイルの読み込み失敗
        if (latest_log_data := LogDict(json.load(f))) is None:
            return await interaction.response.send_message('ファイルの読み込みに失敗しました。', ephemeral=True)

        logs = latest_log_data.get('logs')

        # 無効なID(0未満・ログ数以上、存在しないID)が入力されたらリターン
        if len(logs) <= id < 0 or not exists_log(logs, id):
            return await interaction.response.send_message(utility.error(f'{id} is invalid ID.'), ephemeral=True)

        fixed_log_data = latest_log_data

        for i in range(len(logs)):
            if logs[i].get('id') != id:
                continue
            if logs[i].get('is_cancelled'):
                return await interaction.response.send_message('既にキャンセルされています。', ephemeral=True)
            # 保留中でなければamountを引き、キャンセル
            if not logs[i].get('is_pending'):
                fixed_log_data['pool'] -= logs[i].get('amount')
            fixed_log_data['logs'][i]['is_cancelled'] = True

        with open(file_path, 'w') as f1:
            json.dump(fixed_log_data, f1, indent=4)
        emb = discord.Embed(
            title=f'{utility.inline_code_block(f"#{id}")} 取消',
            description='',
            colour=discord.Colour.light_gray()
        )
        emb.add_field(name='チームプール', value=utility.code_block(format(fixed_log_data.get('pool'), ',')), inline=False)
        emb.set_footer(text='🔥REDZONE🔥')
        await interaction.response.send_message(embed=emb)


@bot.event
async def on_message(message: discord.Message):
    pass

if __name__ == '__main__':
    @bot.event
    async def on_ready():
        await tree.sync()
        await bot.change_presence(
            activity=discord.Streaming(name='CCGTA', url='https://twitch.tv/example'),
            status=discord.Status.online
        )
        print('ok.')

    from core import Core
    core = Core('TOKEN')
    bot.run(core.token) if core.load_environ() else exit(-1)
