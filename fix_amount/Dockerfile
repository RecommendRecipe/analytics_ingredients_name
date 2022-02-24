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
  mecab-ipadic-utf8 \
  nkf

# Pythonの必要なライブラリのインストールZOY
COPY ./requirements.txt $PWD
RUN pip install -r requirements.txt