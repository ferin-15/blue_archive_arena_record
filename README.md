# ブルーアーカイブ 戦術対抗戦 記録ツール
## これは何？
戦術対抗戦の結果のスクリーンショットを認識し、Google SpreadSheetに結果を書き出すツールです。
フォルダに存在するSSの結果を出力する機能とDiscordで投稿されたSSの結果を出力する機能があります。

## 使い方
### 前準備
Python や tesseract.exe や opencv が利用できるように環境構築してください。

保存先の Google SpreadSheet を準備します。
1. ファイルを作ります
2. `入力・攻撃` と `入力・防衛` の2つのシートを用意します
    
Discord Bot を作成します。

`.env` ファイルを作成してください。
```
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
SPREADSHEET_ID=
SPREADSHEET_JSON_PATH=
TESSERACT_PATH=
```

### 実行方法
#### `input_image` フォルダのSSを認識
1. 戦術対抗戦の結果のスクリーンショットを `input_image` フォルダに配置します。
2. `upload_record.py` を実行します

結果
* Google SpreadSheet に結果が出力されます
* 結果が出力されたスクリーンショットは自動で削除されます
* 認識に失敗した画像は削除されずに残ります。以下のような原因が考えられます
    * スクリーンショットがうまく撮影されていない
    * `data/histgram_list.pkl` に該当の生徒のデータが存在しない

#### Discord bot を利用する
1. `discord_bot.py` を実行します
2. Discord のチャンネルにSSを投稿します

結果
* 認識に成功した SS について Google SpreadSheet に結果が出力されます

※ 解像度が1600×900のスクリーンショットにしか対応していません  
※ 対戦相手の先生の名前の認識精度が低いです

## データの準備方法
新しくデータを追加したい場合以下の手順に従ってください。
生徒のアイコン画像のデータを `data/histgram_list.pkl` に保存する方法
1. `character` フォルダの下に生徒名のフォルダを作成します
    * `utils/make_directory.py` を実行することで自動的に作成されます
2. `input_image` フォルダに戦術対抗戦の結果のスクリーンショットを配置します
3. `utils/make_character_image.py` を実行します
4. `character` フォルダの下に生成された画像を生徒名のフォルダの下に移動してください
5. `utils/save_character_hist.py` を実行します
