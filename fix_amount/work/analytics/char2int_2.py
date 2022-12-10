import mojimoji
import pandas as pd
import re
from tqdm import tqdm

tqdm.pandas()

data = pd.read_csv("./data/tmp1_exchanged_data.csv")
print(len(data))
data = data[["id","result","amount"]]

def div_unit(words):
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

data["amount"] = data["amount"].progress_apply(mojimoji.zen_to_han,kana=False,ascii=False)
data[["digit","unit"]] = data["amount"].progress_apply(div_unit)

#print(len(data[data["digit"] == 0])/len(data))

data.to_csv("./data/exchanged_data_rakuten.csv")