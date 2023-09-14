"""
食材名が正規化され、重量がg表記になっているレシピデータの生成
"""
import pandas as pd
from tqdm import tqdm as tq
import json

# 食材データ
ingredients_data = pd.read_csv("./data/exchanged_data_rakuten.csv")
ingredients_data = ingredients_data[["id","result","digit","unit"]]

# レシピデータ
recipe_data = pd.read_csv("./data/rakuten_recipes.csv")
recipe_data = recipe_data[["recipe_id","title","serving_for"]]
recipe_data = recipe_data

# 重量変換表
exchange_map = pd.read_csv("./data/exchange_complete.csv",names=["id","name","etc","unit","g","kind_index"])

finished_recipe_data = {}
finished_recipe_data_num = 0
unit_error = 0
name_error = 0
taken_error = 0

for tmp_racipe in tq(recipe_data.itertuples(),total=len(recipe_data)):
    
    exchange_bool = True
    tmp_ingredients = ingredients_data.query('id == "{}"'.format(tmp_racipe.recipe_id))
    recipe_ingredients = {}

    if len(tmp_ingredients[tmp_ingredients["digit"] == 0]) > 0:
        unit_error += 1
        exchange_bool = False
    elif len(tmp_ingredients[tmp_ingredients["result"].str.contains("#|\?|;|empty")]) > 0: # 忘れがち
        name_error += 1
        exchange_bool = False
    elif len(tmp_ingredients) == 0:
        exchange_bool = False
    else:
        for tmp_ingredient in tmp_ingredients.itertuples():
            try:
                tmp_mapping = exchange_map.query('name == "{}" and unit == "{}"'.format(tmp_ingredient.result,tmp_ingredient.unit))
            except pd.core.computation.ops.UndefinedVariableError:
                print(tmp_ingredients)
                print(tmp_racipe)
                exit(1)

            if tmp_mapping.empty:
                if tmp_ingredient.unit == 'g':
                    recipe_ingredients[tmp_ingredient.result] = float(tmp_ingredient.digit)
                else:
                    exchange_bool = False
                    break
            else:
                try:
                    recipe_ingredients[tmp_ingredient.result] = float(tmp_ingredient.digit) * float(tmp_mapping.iat[0,4])
                except TypeError:
                    print("変換食材:",tmp_ingredient.result)
                    print("変換食材:",tmp_mapping.iat[0,4])
                    exit(1)


    if exchange_bool:
        finished_recipe_data[tmp_racipe.recipe_id] = recipe_ingredients
        finished_recipe_data_num += 1
    else:
        taken_error += 1

print("変換できた数:",finished_recipe_data_num)
print("unit_error:",unit_error)
print("name_error:",name_error)
print("変換できなかった数:",taken_error)


print("変換までクリア")

output = json.dumps(finished_recipe_data,ensure_ascii=False,indent=2)

print("保存直前までクリア")

with open('./data/rakuten_recipe_ingredients.json', "w") as f:
    f.write(output)