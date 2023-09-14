#!/bin/sh
$USER_DIC = /work/user_dic/create_dic.csv
/usr/lib/mecab/mecab-dict-index -d /var/lib/mecab/dic/ipadic/ -u /work/user_dic/user_dic.dic -f utf-8 -t utf-8 $USER_DIC