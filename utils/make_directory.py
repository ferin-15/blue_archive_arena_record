import requests
import re
from bs4 import BeautifulSoup
import os


def get_character_list_from_wiki():
    # ブルーアーカイブのキャラクター一覧ページからキャラクターのリストを取得する
    url = 'https://bluearchive.wikiru.jp/?%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC%E4%B8%80%E8%A6%A7'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    elems = soup.select('#sortabletable1 > tbody')

    # （バニーガール）や（ライディング）は長いのでwikiで改行が入っている分の対応
    elem = re.sub(',（バニー', '（バニー', elems[0].get_text(","))
    elem = re.sub(',（ライディング', '（ライディング', elem)
    elem = re.sub(',（クリスマス', '（クリスマス', elem)
    elem = re.sub(',（キャンプ', '（キャンプ', elem)
    elem = re.sub(',（アイドル', '（アイドル', elem)
    elem = re.sub(',（チーパオ', '（チーパオ', elem)

    flatten_character_list = elem.split(",")

    # 生徒のリストを作成する
    isName = False
    character_list = []
    for i in range(0, len(flatten_character_list)):
        # 生徒の行が★で始まることを利用
        if flatten_character_list[i][0] == '★':
            isName = True
        elif isName:
            character_list.append(flatten_character_list[i])
            isName = False

    return character_list


def make_directory(character_list):
    for character in character_list:
        if not os.path.exists(f'character/{character}'):
            os.makedirs(f'character/{character}')


if __name__ == '__main__':
    character_list = get_character_list_from_wiki()
    make_directory(character_list)