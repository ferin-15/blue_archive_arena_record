FROM python:3.11
WORKDIR /bot

# 更新・日本語化
RUN apt-get update && apt-get -y install locales && apt-get -y upgrade && \
	localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ Asia/Tokyo
ENV TERM xterm

# 必要なシステム依存ライブラリをインストール
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0

# pip install
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot

# ポート開放 (uvicornで指定したポート)
EXPOSE 8080

# 実行
CMD python discord_bot.py