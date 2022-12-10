"""
step3
変換先をidじゃなくて食材名に変更
"""

from tqdm import tqdm as progress
import pandas as pd
import MeCab

# 食材名データの読み込み
data = pd.read_csv("../data/exchange_data/step3_rakuten_in.csv")
# 変換表の読み込み
exchange = pd.read_csv("../data/exchange_before.csv",names=["id","name","plus","unit","g"])
# カナに統一した変換表の読み込み
exchange_kana = pd.read_csv("../data/exchanged_map.csv")

# 必要な情報のみ抽出
exchange_kana = exchange_kana[["id","name"]]
data = data[["id","name","quantity"]]
#data = data.head(1000)
m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")

# 正解データセットをインポート
correct_data = pd.read_excel("../data/correct_data_set.xlsx")

def pick_ingredients(words,m):
  tmp_ingredients = []
  if type(words) != str:
    return None
  else:
    parsed_text = m.parseToNode(words)
    while parsed_text:
      node = parsed_text.feature.split(',')
      # 名詞のみ抽出
      if node[0] == "名詞" and node[2] !="組織":
        try:
          tmp_ingredients.append(node[6])
        except IndexError: # 8番目の要素に読みがない場合
          tmp_ingredients.append( "?" + parsed_text.surface)
      else:
        # 名詞以外は無視
        pass
      parsed_text = parsed_text.next
  length = len(tmp_ingredients)
  if length == 1:
    return tmp_ingredients[0]
  elif length >= 2:
    return ';'.join(tmp_ingredients)
  else:
    return '#'+words

# 進捗を確認
progress.pandas()
# 関数を適応
data['tmp_wakati'] = data['name'].progress_apply(pick_ingredients,m=m)

def exchange_map_ingre(ingredients,exchange):
  # 食材名がない場合
  if ingredients == None:
    return ingredients
  elif '#' in ingredients:
    return ingredients

  ingre = pd.DataFrame([])

  # 複数の食材名候補がある場合
  if ";" in ingredients:
    tmp_ingredients = ingredients.split(";")
    for tmp in tmp_ingredients:
      if "?" in tmp:
        pass
      else:
        # バグを発見
        match_ingre = exchange[exchange["name"] == tmp]
        match_ingre = match_ingre[~match_ingre.duplicated(subset='name')]
        ingre = pd.concat([ingre,match_ingre])
  else:
    # 食材名が一つの時
    if "?" in ingredients:
      return ingredients
    ingre = exchange[exchange["name"] == ingredients]
    ingre = ingre[~ingre.duplicated(subset='name')]
  
  # マッチしてないときのサポート
  if ingre.empty:
    return "empty"
  
  # step2との変更箇所
  # 正解表の中の変換先の列名がresult
  return ';'.join(map(str,ingre["result"].tolist()))

# 関数の適応
data['result'] = data['tmp_wakati'].progress_apply(exchange_map_ingre, exchange=correct_data)
data = data[["id","name","result","quantity"]]
data.to_csv("../data/exchange_data/step3_rakuten.csv")