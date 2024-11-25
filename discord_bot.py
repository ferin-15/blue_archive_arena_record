from dotenv import load_dotenv

import os
import discord
import tempfile

import recognize_arena_result
from server import server_thread

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
load_dotenv()

recognize_arena_result = recognize_arena_result.RecognizeArenaResult()
if os.getenv('ENV') == 'local' or os.getenv('ENV') == 'google_cloud':
    import upload_to_spreadsheet
    upload_to_spreadsheet = upload_to_spreadsheet.UploadToSpreadSheet()


# 結果投稿用の文字列を作成
def make_result_txt(result):
    # 攻撃側が先頭に来るように並び替え
    character_list = result['character_list']
    if not result['is_atk']:
        character_list = character_list[6:] + character_list[:6]

    # 防御側が勝利
    if result['is_atk'] ^ result['is_win']:
        result_txt = f'防御側勝利\n攻撃側：{character_list[:6]}\n防御側：{character_list[6:]}\n'
    # 攻撃側が勝利
    else:
        result_txt = f'攻撃側勝利\n攻撃側：{character_list[:6]}\n防御側：{character_list[6:]}\n'

    return result_txt


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    # bot自身のメッセージには反応しない
    if message.author == client.user:
        return

    # 結果記録用のチャンネルのID
    channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))

    # 対象外のチャンネルの場合反応しない    
    if message.channel.id != channel_id:
        return
    
    # 画像が添付されていない場合反応しない
    if len(message.attachments) == 0:
        return

    # 画像が添付されているかチェック
    result_list = []
    for index, attachment in enumerate(message.attachments, start=1):
        if not attachment.content_type.startswith("image"):
            continue

        # 画像のダウンロード
        image_data = await attachment.read()
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(image_data)
            save_file_path = temp_file.name
            try:
                result = recognize_arena_result.recognize_image(save_file_path)
            except Exception as e:
                await message.channel.send(f'Error: {index} 枚目の画像で認識失敗, {e}')
                continue

        os.remove(save_file_path)

        # 結果を投稿
        result_txt = make_result_txt(result)
        await message.channel.send(result_txt)

        # 入力したプレイヤー名を追加
        result.update({'player_name': message.author.name})
        result_list.append(result)

    if len(result_list) > 0 and os.getenv('ENV') == 'local':
        upload_to_spreadsheet.upload_result_local(result_list)
        await message.channel.send('結果をアップロードしました')
    # koyeb での Google Cloud の認証情報の管理が難しいため、一旦コメントアウト
    # elif len(result_list) > 0 and os.getenv('ENV') == 'koyeb':
    #     upload_to_spreadsheet.upload_result_koyeb(result_list)
    #     await message.channel.send('結果をアップロードしました')
    elif len(result_list) > 0 and os.getenv('ENV') == 'google_cloud':
        upload_to_spreadsheet.upload_result_google_cloud(result_list)
        await message.channel.send('結果をアップロードしました')


# Koyeb用 サーバー立ち上げ
if os.getenv('ENV') == 'koyeb':
    server_thread()

# 実行環境の表示
print(os.getenv('ENV'))

client.run(os.getenv('DISCORD_BOT_TOKEN'))