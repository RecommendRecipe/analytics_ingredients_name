#!/bin/sh
cd dic_install/
# 辞書ファイルの解凍
tar zxfv dic.tar.gz
cd mecab-ipadic-2.7.0-20070801/
# 標準だと文字コードがenc-jpなので変更

#nkf -w --overwrite *.csv
#nkf -w --overwrite *.def
# 文字コードを指定しないとファイルのコードを変えても意味ない
# あと、dicrcの中でconfig-charset = UTF-8という風に書き換えないといけない
./configure --with-charset=utf8
# install
make
make check
make install
# 辞書の格納場所へコピー
cp -r mecab-ipadic-2.7.0-20070801/ /var/lib/mecab/dic/ipadic_latest/
# この後mecabrcの中でdicdir = /var/lib/mecab/dic/ipadic_latest/と変更し、デフォルトの辞書を変更
# 以下はuserdic内での作業
/usr/lib/mecab/mecab-dict-index -d /var/lib/mecab/dic/ipadic_latest/ -u user_dic.dic -f utf-8 -t utf-8 create_dic.csv
echo "おおさじ１" | mecab -d /var/lib/mecab/dic/ipadic_latest/ -u user_dic.dic
# -u 以下のユーザー辞書は同じディレクトリでないと動かない