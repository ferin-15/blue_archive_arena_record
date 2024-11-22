import os
import datetime
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import google.auth

from dotenv import load_dotenv

class UploadToSpreadSheet:
    def __init__(self):
        load_dotenv()

        if os.getenv('ENV') == 'local':
            Auth = os.getenv('SPREADSHEET_JSON_PATH')
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Auth
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(Auth, scope)
            Client = gspread.authorize(credentials)
            self.sheet = Client.open_by_key(os.getenv('SPREADSHEET_ID'))
        elif os.getenv('ENV') == 'koyeb':
            json_data = os.getenv('SPREADSHEET_JSON')
            credentials_dict = json.loads(json_data)
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            Client = gspread.authorize(credentials)
            self.sheet = Client.open_by_key(os.getenv('SPREADSHEET_ID'))
        elif os.getenv('ENV') == 'google_cloud':
            # デフォルトサービスアカウントを利用
            credentials, project = google.auth.default(
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            self.sheet_id = os.getenv('SPREADSHEET_ID')
            self.sheet_name = '入力'


    def upload_result_local(self, result_list):
        date = datetime.datetime.now().strftime('%Y/%m/%d')
        atk_upload_list = []
        def_upload_list = []
        for result in result_list:
            if result['is_atk']:
                atk_upload_list.append(
                    [
                        date,
                        result['enemy_name'],
                        result['is_win'],
                        result['character_list'][0],
                        result['character_list'][1],
                        result['character_list'][2],
                        result['character_list'][3],
                        result['character_list'][4],
                        result['character_list'][5],
                        result['character_list'][6],
                        result['character_list'][7],
                        result['character_list'][8],
                        result['character_list'][9],
                        result['character_list'][10],
                        result['character_list'][11]
                    ]
                )
            else:
                def_upload_list.append(
                    [
                        date,
                        result['enemy_name'],
                        result['is_win'],
                        result['character_list'][0],
                        result['character_list'][1],
                        result['character_list'][2],
                        result['character_list'][3],
                        result['character_list'][4],
                        result['character_list'][5],
                        result['character_list'][6],
                        result['character_list'][7],
                        result['character_list'][8],
                        result['character_list'][9],
                        result['character_list'][10],
                        result['character_list'][11]
                    ]
                )

        self.sheet.values_append("入力・攻撃", {"valueInputOption": "USER_ENTERED"}, {"values": atk_upload_list})
        self.sheet.values_append("入力・防衛", {"valueInputOption": "USER_ENTERED"}, {"values": def_upload_list})


    def upload_result_koyeb(self, result_list):
        date = datetime.datetime.now().strftime('%Y/%m/%d')

        upload_list = []
        for result in result_list:
            # 攻撃側が先頭に来るように並び替え
            character_list = result['character_list']
            if not result['is_atk']:
                character_list = character_list[6:] + character_list[:6]
            
            # 勝利側を判定
            winner = '防御' if result['is_atk'] ^ result['is_win'] else '攻撃'

            # 入力者が攻撃側か防御側か判定
            input_player_side = '攻撃' if result['is_atk'] else '防御'

            upload_list.append(
                [
                    date,
                    result['player_name'],
                    input_player_side,
                    winner,
                    character_list[0],
                    character_list[1],
                    character_list[2],
                    character_list[3],
                    character_list[4],
                    character_list[5],
                    character_list[6],
                    character_list[7],
                    character_list[8],
                    character_list[9],
                    character_list[10],
                    character_list[11]
                ]
            )
            
        self.sheet.values_append("入力", {"valueInputOption": "USER_ENTERED"}, {"values": upload_list})


    def upload_result_google_cloud(self, result_list):
        date = datetime.datetime.now().strftime('%Y/%m/%d')

        upload_list = []
        for result in result_list:
            # 攻撃側が先頭に来るように並び替え
            character_list = result['character_list']
            if not result['is_atk']:
                character_list = character_list[6:] + character_list[:6]
            
            # 勝利側を判定
            winner = '防御' if result['is_atk'] ^ result['is_win'] else '攻撃'

            # 入力者が攻撃側か防御側か判定
            input_player_side = '攻撃' if result['is_atk'] else '防御'

            upload_list.append(
                [
                    date,
                    result['player_name'],
                    input_player_side,
                    winner,
                    character_list[0],
                    character_list[1],
                    character_list[2],
                    character_list[3],
                    character_list[4],
                    character_list[5],
                    character_list[6],
                    character_list[7],
                    character_list[8],
                    character_list[9],
                    character_list[10],
                    character_list[11]
                ]
            )
            
        # データの書き込み範囲を決定
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!A1:P1000'
        ).execute()
        first_empty_row = len(result.get('values', [])) + 1

        # データの書き込み
        range_to_write = f'{self.sheet_name}!A{first_empty_row}'
        body = {
            'values': upload_list
        }
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_to_write,
            valueInputOption='RAW',
            body=body
        ).execute()


if __name__ == '__main__':
    import glob
    import recognize_arena_result
    recognize_arena_result = recognize_arena_result.RecognizeArenaResult()

    warn_path_list = []
    result_list = []
    for path in glob.glob('input_image/*.png'):
        try:
            result = recognize_arena_result.recognize_image(path)
            result_list.append(result)
        except Exception as e:
            print(e)
            warn_path_list.append(path)
            continue

    upload_to_spreadsheet = UploadToSpreadSheet()
    upload_to_spreadsheet.upload_result(result_list)

    # warn_path_list に含まれない画像ファイルを input_image から削除
    for p in glob.glob('input_image/*.png'):
        if p not in warn_path_list:
            os.remove(p)
