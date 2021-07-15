FROM jupyter/base-notebook

USER root
RUN apt-get update
RUN apt-get install -y build-essential \
  curl \
  file \
  git \
  libmecab-dev \
  mecab \
  mecab-ipadic-utf8

RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
RUN mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -y

COPY ./requirements.txt $PWD
RUN pip install -r requirements.txt