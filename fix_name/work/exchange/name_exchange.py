"""
食材名を変換する工程の最終バージョン
"""

from tqdm import tqdm as progress
import pandas as pd
import MeCab

class ExchangeIngredientName():

    def __init__(self,ingredients_pass: str,exchange_pass: str,exchange_kana_pass: str,\
        mecab_pass: str,correct_data_pass: str) -> None:
        
        print("データの読み込みを開始します\n")
        
        # 食材データの読み込み
        self.data = pd.read_csv(ingredients_pass,names=["id","name","quantity"],dtype="str")
        print("欠損処理前のデータの件数:",len(self.data))
        self.data = self.data.dropna(how="any")
        print("欠損処理後のデータ件数:",len(self.data))
        self.data = self.data[["id","name","quantity"]]

        # 変換表の読み込み
        self.exchange = pd.read_csv(exchange_pass,names=["id","name","plus","unit","g"])
        
        # カナに統一した変換表の読み込み
        self.exchange_kana = pd.read_csv(exchange_kana_pass)
        self.exchange_kana = self.exchange_kana[["id","name"]]

        # mecabの設定
        self.mecab = MeCab.Tagger(mecab_pass)

        # 正解データセットをインポート
        self.correct_data = pd.read_excel(correct_data_pass)

        # 進捗を確認
        progress.pandas()

    def pick_ingredients(self,words: str,kana: bool = False):
        """
        形態素に分解するメソッド
        引数のkanaはstep2の時はTrueにし、抽出する部分を変更する
        step1,3の時はFalseにする
        """
        pick_place = 6
        if kana:
            pick_place = 7

        tmp_ingredients = []
        if type(words) != str:
            return None
        else:
            parsed_text = self.mecab.parseToNode(words)
            while parsed_text:
                node = parsed_text.feature.split(',')
                # 名詞のみ抽出
                if node[0] == "名詞" and node[2] !="組織":
                    try:
                        tmp_ingredients.append(node[pick_place])
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

    
    def exchange_map_ingre(self,ingredients: str,step:int=1):
        """
        引数のstepは手順毎に変換表と出力先を指定
        """

        output_area = "name"
        exchange = self.exchange
        if step == 2:
            output_area = "id"
            exchange = self.exchange_kana
        elif step == 3:
            output_area = "result"
            exchange = self.correct_data

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

        return ';'.join(map(str,ingre[output_area].tolist()))
    
    
    def fix_name(self,ingredients: str):

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
                    match_ingre = self.exchange[self.exchange["id"] == int(tmp)]
                    ingre =  pd.concat([ ingre, match_ingre[~match_ingre.duplicated(subset='name')] ])
        else:
            # 食材名が一つの時
            ingre = self.exchange[self.exchange["id"] == int(ingredients)]
            ingre = ingre[~ingre.duplicated(subset='name')]
        if ingre.empty:
            return "empty"

        return ";".join(ingre["name"].tolist())
    
    def progress_start(self) -> None:
        # step1
        self.data["tmp_wakati"] = self.data["name"].progress_apply(self.pick_ingredients)
        self.data["result"] = self.data["tmp_wakati"].progress_apply(self.exchange_map_ingre)
        self.data.drop(columns="tmp_wakati") # 中間結果の削除
        
        step1_done = self.data[~self.data["result"].str.contains("empty|\?")]
        step2_in = self.data[self.data["result"].str.contains("empty|\?")]
        print("step1で変換に成功した食材名:",len(step1_done))
        print("step1で変換できなかったデータ:",len(step2_in))
        step1_done.to_csv("../data/exchange_data/step1_done.csv")
        del step1_done
        step2_in.to_csv("../data/exchange_data/step2_in.csv")
        self.data = step2_in[["id","name","quantity"]]
        del step2_in

        # step2
        self.data["tmp_wakati"] = self.data["name"].progress_apply(self.pick_ingredients,kana=True)
        self.data["tmp_id"] = self.data["tmp_wakati"].progress_apply(self.exchange_map_ingre,step=2)
        self.data["result"] = self.data['tmp_id'].progress_apply(self.fix_name)
        self.data.drop(columns="tmp_wakati") # 中間結果の削除
        self.data.drop(columns="tmp_id") # 中間結果の削除

        step2_done = self.data[~self.data["result"].str.contains("empty|\?")]
        step3_in = self.data[self.data["result"].str.contains("empty|\?")]
        print("step2で変換に成功した食材名:",len(step2_done))
        print("step2で変換できなかったデータ:",len(step3_in))

        self.data = self.data[self.data["result"].str.contains("empty|\?")]
        step2_done.to_csv("../data/exchange_data/step2_done.csv")
        step3_in.to_csv("../data/exchange_data/step3_in.csv")
        del step2_done
        self.data = step3_in[["id","name","quantity"]]
        del step3_in

        # step3
        self.data["tmp_wakati"] = self.data["name"].progress_apply(self.pick_ingredients)
        self.data["result"] = self.data["tmp_wakati"].progress_apply(self.exchange_map_ingre,step=3)

        self.data.drop(columns="tmp_wakati") # 中間結果の削除
        step1_data = pd.read_csv('../data/exchange_data/step1_done.csv',dtype="str")
        step2_data = pd.read_csv('../data/exchange_data/step2_done.csv',dtype="str")
        step3_data = self.data
        fixed_name_data = pd.concat([step1_data,step2_data,step3_data])
        fixed_name_data = fixed_name_data[["id","result","quantity"]]
        fixed_name_data.to_csv("../data/exchange_data/fixed_name_data_rakuten.csv")
        print("done.")
    
if __name__ == "__main__":

    exchange_unit = ExchangeIngredientName("../data/rakuten_ingredients.csv",\
                                            "../data/exchange_before.csv",\
                                            "../data/exchange_map.csv",\
                                            "-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd",\
                                            "../data/correct_data_set.xlsx")

    exchange_unit.progress_start()