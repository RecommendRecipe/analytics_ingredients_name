import pandas as pd
import mojimoji
import MeCab
from tqdm import tqdm as progress
import unicodedata
from kanjize import kanji2int
import re
import logging
import sys

class Amount2Digit():

    def __init__(self,ingrediens_path: str,flag:str) -> None:
        self.logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("分量単位変換クラスの初期化を行います。")

        # 変換データの読み込み
        self.data = pd.read_csv(ingrediens_path,dtype="str")
        self.logger.info("生データの総数:{}".format(len(self.data)))

        # 変換データの前処理
        self.data = self.data.dropna(subset=["result"])
        self.data = self.data.sort_values("id")
        self.data = self.data.fillna("わからん")
        self.data["quantity"] = self.data["quantity"].apply(mojimoji.han_to_zen)

        # 形態素解析器
        self.tokenizer =  MeCab.Tagger("-d /var/lib/mecab/dic/ipadic_latest/ -u ./data/user_dic.dic")

        # データのタグ（例:rakuten）
        self.flag = flag
    def pick_amount(self,raw_amount :str) -> str:
        """
        seq_candidate_amount
        変換候補となる数詞を格納
        複数の数詞で構成される語（例：12）などは
        数詞以外の語が来るまでを連結して格納
        区切りは＊
        """
        seq_candidate_amount = []

        """
        実際に数字に変換する文字を格納
        """
        #done_amount = []

        parsed_text = self.tokenizer.parseToNode(raw_amount) # mecabで形態素に分解
        tmp_diget = ""                                       # 処理中の数字を格納
        operator = ""                                        # /などの演算子を含む場合の判定
        
        try:
            while parsed_text:
                node = parsed_text.feature.split(',')
                if node[1] == "数":
                    # 演算子の処理
                    if len(operator) > 0 and len(tmp_diget) > 0:
                        tmp_diget += operator
                        operator = ""

                    tmp_diget += parsed_text.surface
                elif node[2] == "助数詞":
                    if len(tmp_diget) !=0:
                        tmp_diget += ';' + node[6]
                        seq_candidate_amount.append(tmp_diget)
                        tmp_diget = ""
                    else:
                        pass
                else:
                    if node[6] == "/" or node[6] == "／":
                        operator = node[6]
                    else:
                        tmp_diget = ""
            
                parsed_text = parsed_text.next
            return "_".join(seq_candidate_amount)
        except TypeError:
            return "undefined"

    def pick_amount_sazi(self,raw_amount: str) -> str:
        """
        seq_candidate_amount
        変換候補となる数詞を格納
        複数の数詞で構成される語（例：12）などは
        数詞以外の語が来るまでを連結して格納
        区切りは＊
        """
        seq_candidate_amount = []

        """
        実際に数字に変換する文字を格納
        """
        #done_amount = []

        parsed_text = self.tokenizer.parseToNode(raw_amount) # mecabで形態素に分解
        tmp_diget = ""                          # 処理中の数字を格納
        sazi = ""
        
        try:
            while parsed_text:
                node = parsed_text.feature.split(',')
                if node[1] == "数" or node[6] == "／" or node[1] == "サ変接続":
                    tmp_diget += parsed_text.surface

                elif node[2] == "助数詞":
                    tmp_diget = ""
                    sazi = node[6]
                else:
                    if len(sazi) != 0 and len(tmp_diget) != 0:
                        tmp_diget +=";" + sazi
                        seq_candidate_amount.append(tmp_diget)
                        sazi = ""
                    
                parsed_text = parsed_text.next
            return "_".join(seq_candidate_amount)
        except TypeError:
            return "undefined"
    
    def kanji2degit(self,words : str) -> str:
        if words == "ダメ" or "_" or "" in words :
            return words
        
        finish_words = ""
        tmp_kanzi = ""

        iter_n = 0
        work = words.split(";")[0]
        for degit in work:
            iter_n += 1
            if unicodedata.east_asian_width(degit) == "W":
                tmp_kanzi += degit
                if iter_n == len(work):
                    finish_words += str(kanji2int(tmp_kanzi))
                    
            else:
                if len(tmp_kanzi) != 0:
                    finish_words += str(kanji2int(tmp_kanzi))
                    tmp_kanzi = ""
                finish_words += degit
        
        return finish_words + ";" + words.split(";")[1]
    
    def culuculate(self,words:str) -> str:
        if words == "ダメ" or "_" or "" in words:
            return words
        elif "／" not in words and "\\" not in words:
            return words
        elif ";" not in words:
            return "ダメ"
        
        ch_degit = ""
        mo_degit = ""
        finish_words = ""
        work = words.split(";")[0]
        cul_bool = False
        iter_n = 0

        for degit in work:
            iter_n += 1

            if degit == "／" or degit == "\\":
                cul_bool = True
                
            elif re.match("[0-9０-９.．]",degit) is not None:
                if cul_bool:
                    mo_degit += mojimoji.zen_to_han(degit)
                else:
                    ch_degit += mojimoji.zen_to_han(degit)
                
                if iter_n == len(work) and len(finish_words) == 0:
                    try:
                        finish_words += str(float(ch_degit) / float(mo_degit))
                    except ZeroDivisionError:
                        return "おかしい"
                    except ValueError:
                        return "数字抜け"

            else:
                if len(mo_degit) != 0 and len(ch_degit) != 0:
                    finish_words += str(float(ch_degit) / float(mo_degit))
                    ch_degit = ""
                    mo_degit = ""
                finish_words += degit

        return finish_words + ";" + words.split(";")[1]
    
    def exchange_range(self,words: str) -> str:
        if words == "ダメ" or words == "数字抜け" or words == "おかしい" or "_" or "" in words:
            return words
        elif "～" not in words and "－" not in words and "，" not in words and "、" not in words:
            return words
            
        ch_degit = ""
        mo_degit = ""
        finish_words = ""
        work = words.split(";")[0]
        cul_bool = False
        iter_n = 0

        for degit in work:
            iter_n += 1

            if degit == "～" or degit == "－" or degit == "，" or degit == "、" :
                cul_bool = True
                if len(work) == iter_n:
                    finish_words += mo_degit
                    finish_words += ch_degit
                
            elif re.match("[0-9０-９.]",degit) is not None:
                if cul_bool:
                    mo_degit += mojimoji.zen_to_han(degit)
                else:
                    ch_degit += mojimoji.zen_to_han(degit)
                
                if iter_n == len(work) and len(finish_words) == 0:
                    if len(mo_degit) != 0 and len(ch_degit) != 0:
                        finish_words += str( ( float(ch_degit) + float(mo_degit) ) / 2)
                    elif len(mo_degit) == 0 or len(ch_degit) == 0:
                        finish_words += mo_degit
                        finish_words += ch_degit
            else:
                pass
        
        if finish_words == "":
            return "ダメ"
        return finish_words + ";" + words.split(";")[1]
    

    def div_unit(self,words: str) -> pd.Series:
        tmp_degit = words.split(";")[0]
        if words == "ダメ" or words == "数字抜け" or words == "おかしい" or "_" in words or tmp_degit == '':
            tmp_degit = "0"
            unit = "使えない"
        else:
            unit = words.split(";")[1]

            if re.fullmatch("[0-9０-９.]*",tmp_degit) is None:
                tmp_degit = "0"
                unit = "使えない"

        return pd.Series([float( mojimoji.zen_to_han(tmp_degit) ),unit] )
    
    def progress_start(self) -> None:
        
        progress.pandas()   # 進捗を確認するモジュールを配置

        # 数値と単位を分離（ノーマル）
        self.data['amount'] = self.data['quantity'].progress_apply(self.pick_amount)

        # 数値と単位を分離（大匙などに対応）
        sazi_data = self.data[~self.data["amount"].str.contains(';')]
        sazi_data['quantity'] = sazi_data['quantity'].progress_apply(mojimoji.zen_to_han,kana=False,ascii=False)
        sazi_data["amount"] = sazi_data['quantity'].progress_apply(self.pick_amount_sazi)

        self.data = pd.concat([sazi_data,self.data[self.data["amount"].str.contains(';')]])
        save_path = "./data/divide_unit_data_" + self.flag + ".csv"
        self.data.to_csv(save_path)

        """
        ここからは分離した数値を計算可能なfloat型に直す処理
        """

        self.data = pd.read_csv(save_path)
        self.data = self.data[["id","result","amount"]]
        self.data = self.data.fillna("ダメ")
        self.data = self.data.sort_values("id")
        print(self.data.head(5))
        self.data["amount"] = self.data["amount"].progress_apply(self.kanji2degit)
        self.data["amount"] = self.data["amount"].progress_apply(self.culuculate)
        self.data["amount"] = self.data["amount"].progress_apply(self.exchange_range)
        self.data["amount"] = self.data["amount"].progress_apply(mojimoji.zen_to_han,kana=False,ascii=False)
        self.data[["digit","unit"]] = self.data["amount"].progress_apply(self.div_unit)

        # 保存
        save_path = "./data/exchanged_data_" + self.flag + ".csv"
        self.data.to_csv(save_path)

if __name__ == "__main__":
    test = Amount2Digit("./data/fixed_name_data_rakuten.csv","rakuten")
    test.progress_start()