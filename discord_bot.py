from dotenv import load_dotenv

import os
import discord
import tempfile

import recognize_arena_result

if os.getenv('ENV') == 'private':
    import upload_to_spreadsheet

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
load_dotenv()

recognize_arena_result = recognize_arena_result.RecognizeArenaResult()
if os.getenv('ENV') == 'private':
    upload_to_spreadsheet = upload_to_spreadsheet.UploadToSpreadSheet()

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

    if message.channel.id == channel_id:
        # 画像が添付されているかチェック
        if len(message.attachments) > 0:
            result_list = []
            for index, attachment in enumerate(message.attachments, start=1):
                if attachment.content_type.startswith("image"):
                    # 画像のダウンロード
                    image_data = await attachment.read()
                    # 一時ファイルとして保存
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(image_data)
                    save_file_path = temp_file.name

                    try:
                        result = recognize_arena_result.recognize_image(save_file_path)
                        
                        is_atk = '攻撃' if result['is_atk'] else '防御'
                        is_win = '勝利' if result['is_win'] else '敗北'
                        character_list = result['character_list']

                        # 攻撃側が先頭に来るように並び替え
                        if not result['is_atk']:
                            character_list = character_list[6:] + character_list[:6]

                        # 攻撃側が勝利
                        if (is_atk and is_win) or (not is_atk and not is_win):
                            await message.channel.send(
                                f'攻撃側勝利\n{character_list}'
                            )
                        # 防御側が勝利
                        else:
                            await message.channel.send(
                                f'防御側勝利\n{character_list}'
                            )

                    except Exception as e:
                        await message.channel.send(f'Error: {index} 枚目の画像で認識失敗, {e}')
                        continue
                    
                    if os.getenv('ENV') == 'private':
                        result_list.append(result)
            
            if len(result_list) > 0 and os.getenv('ENV') == 'private':
                upload_to_spreadsheet.upload_result(result_list)
                await message.channel.send('結果をアップロードしました')


client.run(os.getenv('DISCORD_BOT_TOKEN'))