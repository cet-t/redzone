import asyncio
from typing import Optional
import discord
import json
import os
from datetime import datetime
from random import randint


from data.member_data import *
from data.heist_data import *
from parameter import Parameter, LogDict, LogDataDict
import utility

bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)


@tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(title='Pong!', description=''))


@tree.command()
@discord.app_commands.describe(count='count')
async def dice(interaction: discord.Interaction, count: int = 1):
    pool = ['one', 'two', 'three', 'four', 'five', 'six']
    result: list[str] = []
    for _ in range(count):
        result.append(f':{utility.Random.choice_item(pool)}:')
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
        return await interaction.response.send_message(embed=Parameter.Embed.error('権限がありません。'), ephemeral=True)
    await interaction.response.send_message(embed=Parameter.Embed.log('10秒後にオフラインになります。'), ephemeral=True)
    await asyncio.sleep(10)
    await asyncio.run(exit(0))


@tree.command()
@discord.app_commands.describe(member='メンバー')
async def user_info(interaction: discord.Interaction, member: discord.Member):
    pass


@tree.command(name='cost', description='経費精算, チームプール管理')
@discord.app_commands.describe(amount='金額', note='支払内容')
async def cost_production(interaction: discord.Interaction, amount: int, note: Optional[str] = None):
    # 専用チャンネル外で使用
    if not interaction.channel_id in Parameter.COST_CHANNEL_ID.values():
        return await interaction.response.send_message(
            embed=Parameter.Embed.warning(
                f'{utility.Discord.mention(Parameter.COST_CHANNEL_ID.get("redzone"), utility.Discord.Mention.channel)}で使用してください。'),
            ephemeral=True)
    # ファイルが存在しない
    if not os.path.exists(Parameter.LOG_FILE_PATH):
        return await interaction.response.send_message(embed=Parameter.Embed.error(f'ログファイルが存在しません。'), ephemeral=True)

    with open(Parameter.LOG_FILE_PATH, 'r') as f:
        if (load_data := LogDict(json.load(f))) is None:
            return await interaction.response.send_message(embed=Parameter.Embed.error('ファイルを読み込めませんでした。'), ephemeral=True)

        pool = load_data.get(Parameter.Key.Log.POOL)
        logs = load_data.get(Parameter.Key.Log.LOGS)

        # ボスが使用した場合は直ぐ金額を反映
        if is_boss := (interaction.user.id in Parameter.ADMIN_USER_ID.values()):
            pool += amount

        log = LogDataDict(
            id=len(logs),
            datetime=datetime.now().isoformat(),
            user_id=interaction.user.id,
            amount=amount,
            note=note,
            is_cancelled=False,
            is_pending=not is_boss,
            message_id=interaction.id
        )
        logs.append(log)
        load_data = LogDict(pool=pool, logs=logs)

        with open(Parameter.LOG_FILE_PATH, 'w') as ff:
            json.dump(load_data, ff, indent=4)
            emb = discord.Embed(
                title=utility.Discord.inline_code_block(f"#{log.get(Parameter.Key.LogData.ID)}") + (utility.String.empty if is_boss else Parameter.Text.PENDING),
                description='',
                color=discord.Color.blue() if amount >= 0 else discord.Color.brand_red()
            )
            emb.add_field(name=Parameter.Text.AMOUNT, value=utility.Discord.code_block(format(amount, ',')), inline=False)
            if note is not None:
                emb.add_field(name=Parameter.Text.NOTE, value=utility.Discord.code_block(note), inline=False)
            emb.add_field(name=Parameter.Text.POOL, value=utility.Discord.code_block(format(pool, ',')), inline=False)
            emb.set_footer(text=Parameter.Text.footer())

            await interaction.response.send_message(embed=emb)


def exists_log(logs: list[LogDataDict], log_id: int) -> bool:
    for log in logs:
        if log.get(Parameter.Key.LogData.ID) == log_id:
            return True
    return False


@tree.command(name='cancel', description='取消')
@discord.app_commands.describe(id='log_id')
async def cost_cancel(interaction: discord.Interaction, id: int):
    if not interaction.channel_id in Parameter.COST_CHANNEL_ID.values():
        return await interaction.response.send_message(
            embed=Parameter.Embed.warning(f'{utility.Discord.mention(Parameter.COST_CHANNEL_ID.get("redzone"), utility.Discord.Mention.channel)}で使用してください。'),
            ephemeral=True
        )

    with open(Parameter.LOG_FILE_PATH, 'r') as f:
        # ログファイルの読み込み失敗
        if ((latest_data := LogDict(json.load(f)))) is None:
            return await interaction.response.send_message(embed=Parameter.Embed.error('ファイルの読み込みに失敗しました。'), ephemeral=True)

        logs = latest_data.get(Parameter.Key.Log.LOGS)

        # 無効なID(0未満・ログ数以上、存在しないID)が入力されたらリターン
        if len(logs) <= id < 0 or not exists_log(logs, id):
            return await interaction.response.send_message(embed=Parameter.Embed.error(f'{utility.Discord.inline_code_block(f"#{id}")} is invalid ID.'), ephemeral=True)

        fixed_data = latest_data

        for i in range(len(logs)):
            if logs[i].get(Parameter.Key.LogData.ID) != id:
                continue
            if logs[i].get(Parameter.Key.LogData.IS_CANCELLED):
                return await interaction.response.send_message(embed=Parameter.Embed.warning('既にキャンセルされています。'), ephemeral=True)

            # 保留中でなければamountを引き、キャンセル
            if not logs[i].get(Parameter.Key.LogData.IS_PENDING):
                fixed_data[Parameter.Key.Log.POOL] -= logs[i].get(Parameter.Key.LogData.AMOUNT)
            fixed_data[Parameter.Key.Log.LOGS][i][Parameter.Key.LogData.IS_CANCELLED] = True

        with open(Parameter.LOG_FILE_PATH, 'w') as f1:
            json.dump(fixed_data, f1, indent=4)
        emb = discord.Embed(title=f'{utility.Discord.inline_code_block(f"#{id}")} {Parameter.Text.CANCEL}', description='', colour=discord.Colour.light_gray())
        emb.add_field(name=Parameter.Text.POOL, value=utility.Discord.code_block(format(fixed_data.get(Parameter.Key.Log.POOL), ',')), inline=False)
        emb.set_footer(text=Parameter.Text.footer())
        await interaction.response.send_message(embed=emb)


@bot.event
async def on_message(message: discord.Message):
    pass


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # https://discordpy.readthedocs.io/ja/latest/api.html?highlight=on_raw_reaction_add#discord.on_raw_reaction_add

    # 専用チャンネル外、指定のユーザー以外
    if not payload.channel_id in Parameter.COST_CHANNEL_ID.values() or not payload.member.id in Parameter.ADMIN_USER_ID.values():  # type: ignore
        return

    is_accepted: Optional[bool] = None
    target_log_data: Optional[LogDataDict] = None

    # 承認
    if payload.emoji.name in Parameter.Emoji.ACCEPT:
        is_accepted = True

        # リアクションされたチャンネルを取得
        channel = bot.get_channel(payload.channel_id)
        # チャンネルからメッセージを取得
        message = await channel.fetch_message(payload.message_id)  # type: ignore

        if message is not None:
            with open(Parameter.LOG_FILE_PATH, 'r') as fread:
                # ファイルを読み込み変数に格納
                log = LogDict(json.load(fread))
                pool, logs = log.get(Parameter.Key.Log.POOL), log.get(Parameter.Key.Log.LOGS)

                for i in range(len(logs)):
                    # 対象のメッセージ、保留中
                    if logs[i].get(Parameter.Key.LogData.MESSAGE_ID) == message.id and logs[i].get(Parameter.Key.LogData.IS_PENDING):
                        # 保留中フラグを解除
                        logs[i][Parameter.Key.LogData.IS_PENDING] = False
                        # チームプールにamountを足す
                        pool += logs[i].get(Parameter.Key.LogData.AMOUNT)
                        # 対象のログ
                        target_log_data = logs[i]

                with open(Parameter.LOG_FILE_PATH, 'w') as fwrite:
                    # 修正したデータを書き込み
                    json.dump(LogDict(pool=pool, logs=logs), fwrite, indent=4)
    # 拒否
    elif payload.emoji.name in Parameter.Emoji.REJECT:
        is_accepted = False
    # 無効な絵文字
    else:
        return

    # 承認/拒否された場合
    if is_accepted is not None and target_log_data is not None:
        emb = discord.Embed(
            title=f'{utility.Discord.inline_code_block(f"#{target_log_data.get(Parameter.Key.LogData.ID)}")} {Parameter.Text.ACCEPT if is_accepted else Parameter.Text.REJECT}',
            description='',
            colour=discord.Colour.green() if is_accepted else discord.Colour.red()
        )
        # 承認された場合はチームプールを表示
        if is_accepted:
            emb.add_field(name=Parameter.Text.POOL, value=utility.Discord.code_block(format(target_log_data.get(Parameter.Key.Log.POOL), ',')), inline=False)
        # noteがあれば表示
        if utility.String.is_none_or_empty(note := target_log_data.get(Parameter.Key.LogData.NOTE)):
            emb.add_field(name=Parameter.Text.NOTE, value=utility.Discord.code_block(str(note)))
        emb.set_footer(text=Parameter.Text.footer())
        await message.channel.send(embed=emb)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
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
    bot.run(core.token) if (core := Core(Parameter.TOKEN)).load_token() else exit(-1)
