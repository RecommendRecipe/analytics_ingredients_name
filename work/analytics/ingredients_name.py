"""
食材名を解析するスクリプトです。
"""
import pandas as pd
import MeCab
from tqdm import tqdm as progress

# 食材名データの読み込み
data = pd.read_csv("../data/recommend_ingredients.csv",names=["id","name","quantity"])
# 変換表の読み込み
exchange = pd.read_csv("../data/exchange_before.csv",names=["id","name","plus","unit","g"])
# カナに統一した変換表の読み込み
exchange_kana = pd.read_csv("../data/exchanged_map.csv")

# 必要な情報のみ抽出
exchange_kana = exchange_kana[["id","name"]]
data = data[["id","name"]]

m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")

"""
食材名から名詞部分を抜き出す関数
名詞が一つの場合はその読みを返す。
入力が文字列でない場合はNoneを返す
複数の名詞がある場合には区切り文字を;にして連結する
名詞ではあるが、,を区切り文字とした場合に辞書の8番目に読みがない場合は
先頭に?をつけて返している。
名詞がない場合は引数の先頭に#を付けて返す
"""
def pick_ingredients(words,m):
  tmp_ingredients = []
  if type(words) != str:
    return None
  else:
    parsed_text = m.parseToNode(words)
    while parsed_text:
      node = parsed_text.feature.split(',')
      # 名詞のみ抽出
      if node[0] == "名詞":
        try:
          tmp_ingredients.append(node[7])
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
data['kana_name'] = data['name'].progress_apply(pick_ingredients,m=m)


"""
変換表からカナに変換した食材名
を検索、その結果を返す。
結果は変換表のidが文字列で返される。
複数の候補がある場合は"id;id..."といった形のひとつの文字列として返される。
"""
def exchange_map_ingre(ingredients,exchange_map):
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
        match_ingre = exchange_map[exchange_map["name"] == tmp]
        ingre = ingre.append(match_ingre[~match_ingre.duplicated(subset='name')])
  else:
    # 食材名が一つの時
    if "?" in ingredients:
      return ingredients
    ingre = exchange_map[exchange_map["name"] == ingredients]
    ingre = ingre[~ingre.duplicated(subset='name')]
  
  # マッチしてないときのサポート
  if ingre.empty:
    return "empty"

  return ';'.join(map(str,ingre["id"].tolist()))

# 関数の適応
data['fix_kana_name'] = data['kana_name'].progress_apply(exchange_map_ingre, exchange_map=exchange_kana)

def fix_name(ingredients,exchange):
  if ingredients == None:
    return ingredients
  if ingredients == "empty" or "?" in ingredients or "#" in ingredients:
    return ingredients
  ingre = pd.DataFrame([])
  if ";" in ingredients:
    tmp_ingredients = ingredients.split(";")
    for tmp in tmp_ingredients:
      if "?" in tmp:
        pass
      else:
        match_ingre = exchange[exchange["id"] == int(tmp)]
        ingre = ingre.append(match_ingre[~match_ingre.duplicated(subset='name')])
  else:
    # 食材名が一つの時
    ingre = exchange[exchange["id"] == int(ingredients)]
    ingre = ingre[~ingre.duplicated(subset='name')]
  return ";".join(ingre["name"].tolist())

data['fixed_name'] = data['fix_kana_name'].progress_apply(fix_name, exchange=exchange)

data.to_csv("../data/analitics_data.csv")