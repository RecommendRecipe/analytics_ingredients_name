FROM jupyter/base-notebook

USER root
RUN apt-get update
# いろいろでいじなものをインストールZOY
RUN apt-get install -y build-essential \
  curl \
  file \
  git \
  libmecab-dev \
  mecab \
  mecab-ipadic-utf8

# 形態素解析の辞書のインストールZOY
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
RUN mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -y

# Pythonの必要なライブラリのインストールZOY
COPY ./requirements.txt $PWD
RUN pip install -r requirements.txt