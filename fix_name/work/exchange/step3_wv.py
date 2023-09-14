from gensim.models import KeyedVectors
import pandas as pd
import MeCab

# 学習データの読み込み
recipe_wv = KeyedVectors.load_word2vec_format('../data/trained_data/cookpad_m1_v500_min5_w4.vec.pt', binary=True)

from tqdm import tqdm as progress

m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
# データの読み込み
exchange_kana = pd.read_csv("../data/exchanged_map.csv",encoding='utf-8')
uncorrect_ingredients_data = pd.read_csv("../data/exchange_data/step3_in.csv",encoding='utf-8')
uncorrect_ingredients_data = uncorrect_ingredients_data[["id","name"]]

#uncorrect_ingredients_data = uncorrect_ingredients_data.head(1000)

def simi_search(word,exchange_kana,wv,m):
  
  try:
    # 類似語の取得
    ingre_list = wv.most_similar(positive=[word])
  except KeyError:
    # 検索できない場合は"keyerror"を返す
    return pd.Series(["keyerror",99])
  
  for index,tmp in enumerate(ingre_list):
    tmp_ingre_name = m.parseToNode(tmp[0])
    ingre_name = []
    while tmp_ingre_name:
      node = tmp_ingre_name.feature.split(',')
      # 名詞のみ抽出
      if node[0] == "名詞":
        try:
          ingre_name.append(node[7])
        except IndexError: # 8番目の要素に読みがない場合
          pass
      else:
        # 名詞以外は無視ZOOOY
        pass
      tmp_ingre_name = tmp_ingre_name.next
    ingre = exchange_kana[exchange_kana["name"] == ''.join(ingre_name)]
    
    if ingre.empty:
      pass
    else:
      #とりあえず一個見つかったら食材名が決定ZOY
      ingre = ingre[~ingre.duplicated(subset='name')]
      return pd.Series([';'.join(map(str,ingre["name"].tolist())),index])

  #for文の終了
  return pd.Series(["empty",99])

# 進捗を確認
progress.pandas()

uncorrect_ingredients_data[["result","rank"]] = uncorrect_ingredients_data["name"].progress_apply(simi_search, exchange_kana=exchange_kana, wv=recipe_wv, m=m)
uncorrect_ingredients_data.to_csv("../data/exchange_data/step3_w2v_result.csv",encoding='utf-8')