"""
食材名が正規化され、重量がg表記になっているレシピデータの生成
"""
import pandas as pd
from tqdm import tqdm
import re

tqdm.pandas()

# 食材データ
ingredients_data = pd.read_csv("./data/exchanged_data.csv")
print(len(ingredients_data))
ingredients_data = ingredients_data[["id","result","digit","unit"]]

# 重量変換表
exchange_map = pd.read_csv("./data/exchange.csv",names=["id","name","etc","unit","g"])

def check_amount(ingredient: tuple,exchange: pd.DataFrame):
    if ingredient.digit == 0:
        return False
    
    if re.search("#|\?|;|empty",ingredient.result):
        return False
    
    search_ingredient = \
        exchange.query('name == "{}" and unit == "{}"'.format(ingredient.result,ingredient.unit))
    
    if search_ingredient.empty:
        if ingredient.unit == 'g':
            return True
        return False
    else:
        return True

ingredients_data["check"] = ingredients_data.progress_apply(check_amount,exchange=exchange_map,axis=1)
print(len(ingredients_data[ingredients_data["check"] == True])/len(ingredients_data))
