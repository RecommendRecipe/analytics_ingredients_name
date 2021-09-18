from gensim.models import KeyedVectors
import pandas as pd
import MeCab

# 学習データの読み込み
recipe_wv = KeyedVectors.load_word2vec_format('../data//trained_data/GloVe/input_glove_vector_5_600.vec.pt', binary=False)

from tqdm import tqdm as progress

m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
# データの読み込み
exchange_kana = pd.read_csv("../data/exchanged_map.csv",encoding='utf-8')
uncorrect_ingredients_data = pd.read_csv("../data/exchange_data/step3_in.csv",encoding='utf-8')
uncorrect_ingredients_data = uncorrect_ingredients_data[["id","name"]]

#uncorrect_ingredients_data = uncorrect_ingredients_data.head(50)

def simi_search(word,exchange_kana,wv,m):
  
  try:
    # 類似語の取得
    ingre_list = wv.most_similar(positive=[word])
  except KeyError:
    # 検索できない場合は"keyerror"を返す
    return 'keyerror'
  
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
      ingre["name"] += " " + str(index)
      return ';'.join(map(str,ingre["name"].tolist()))

  #for文の終了
  return "empty"

# 進捗を確認
progress.pandas()

uncorrect_ingredients_data["result"] = uncorrect_ingredients_data["name"].progress_apply(simi_search, exchange_kana=exchange_kana, wv=recipe_wv, m=m)
uncorrect_ingredients_data.to_csv("../data/exchange_data/step3_glove.csv",encoding='utf-8')