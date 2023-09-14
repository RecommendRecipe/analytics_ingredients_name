"""
分量の部分を数字に変換
1 漢数字を数字に変換
2 
"""
import pandas as pd

data = pd.read_csv("./data/fix_data_rakuten.csv")
print(len(data))
data = data.fillna("ダメ")
data = data[["id","result","amount"]]

"""
漢数字を数字に
"""

import unicodedata
from kanjize import kanji2int

def kanji2degit(words):
    if words == "ダメ" or "_" in words :
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
    
from tqdm import tqdm
tqdm.pandas()
data["amount"] = data["amount"].progress_apply(kanji2degit)

"""
/の演算を行う
"""
import mojimoji
import re
def culuculate(words):
    if words == "ダメ" or "_" in words:
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
data["amount"] = data["amount"].progress_apply(culuculate)

"""
~
"""

import mojimoji
import re
def exchange_range(words):
    if words == "ダメ" or words == "数字抜け" or words == "おかしい" or "_" in words:
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

data["amount"] = data["amount"].progress_apply(exchange_range)

# ここから先はメモリが死ぬのでいったん作業を保存

data.to_csv("./data/tmp1_exchanged_data.csv")