from tqdm import tqdm as progress
import pandas as pd
import MeCab

# 食材名データの読み込み
data = pd.read_csv("../data/fixed_recommend_ingredients.csv", dtype="str")
# 欠損値の処理
print(len(data))
data = data.dropna(how='any')
print("欠損値除外後",len(data))
# 変換表の読み込み
exchange = pd.read_csv("../data/exchange_before.csv",names=["id","name","plus","unit","g"])
# カナに統一した変換表の読み込み
exchange_kana = pd.read_csv("../data/exchanged_map.csv")

# 必要な情報のみ抽出
exchange_kana = exchange_kana[["id","name"]]
data = data[["id","name","quantity"]]
#data = data.head(1000)
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

"""
変換表からカナに変換した食材名
を検索、その結果を返す。
結果は変換表の食材名が文字列で返される。
複数の候補がある場合は"id;id..."といった形のひとつの文字列として返される。
候補がない場合はempty
"""

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

  return ';'.join(map(str,ingre["name"].tolist()))


# 関数の適応
data['result'] = data['tmp_wakati'].progress_apply(exchange_map_ingre, exchange=exchange)
data = data[["id","result","quantity","name"]]
data.to_csv("../data/exchange_data/step1.csv")