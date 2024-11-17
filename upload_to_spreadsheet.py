import os
import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from dotenv import load_dotenv

class UploadToSpreadSheet:
    def __init__(self):
        load_dotenv()
        Auth = os.getenv('SPREADSHEET_JSON_PATH')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Auth
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(Auth, scope)
        Client = gspread.authorize(credentials)
        self.sheet = Client.open_by_key(os.getenv('SPREADSHEET_ID'))


    def upload_result(self, result_list):
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
