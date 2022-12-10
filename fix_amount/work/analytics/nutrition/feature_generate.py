"""
推薦や分析で用いる特徴ベクトルの作成を行うクラスです
"""
import pandas as pd
import json
import numpy as np
from tqdm import tqdm as tq

class FeatureGenerate():
    
    def __init__(self,nutrition_path : str,\
                    exchange_path: str,flag: str,\
                        ingredients: str,recipe_info_path: str) -> None:
        
        # 栄養素変換用の読み込みと前処理
        tmp = pd.read_csv(nutrition_path)
        tmp = tmp[["id","kcal","water","prot",\
                "chole","fat","fib","polyl","na","k","ca","mg","p","fe","zn","cu","mn",\
                    "iodine","se","cr","mo","vitd","vitk","thla","ribf","nia","vitb12","fol",\
                        "pantac","biot","vitc"]]
                        
        self.nutrition = tmp.astype(float)
        del tmp

        # 重量単位変換表の読み込み

        self.exchange_amount = pd.read_csv(exchange_path,names=["id","name","additonal","unit","g","kind"])
        self.flag = flag

        # 変換、正規化する食材情報
        with open(ingredients,"r") as f:
            self.ingre = json.load(f)

        # 正規化する際の情報
        self.recipe_info = pd.read_csv(recipe_info_path)
        self.recipe_info = self.recipe_info[["recipe_id","title","serving_for"]]


    def reguration_ingredients(self):
        """
        食材データを何人前かの情報で正規化
        また、その結果をjson形式で保存
        """
        cleaned_recipes ={}

        for recipe in tq(self.ingre.items(), total=len(self.ingre)):
        
            serving_for = self.recipe_info[self.recipe_info["recipe_id"] == recipe[0]].values[0][2]
            tmp = {}
            for ingredient in recipe[1].items():
                tmp[ingredient[0]] = ingredient[1] / serving_for
            
            cleaned_recipes[recipe[0]] = tmp

        output_path = "./cleaned_" + self.flag +"_ingredients.json"

        with open(output_path,"w") as f:
            f.write(json.dumps(cleaned_recipes,ensure_ascii=False,indent=2))
        self.ingre = cleaned_recipes


    def generate_nutrition(self) -> None:
        """
        栄養素ベクトルを生成して出力
        """

        fixed_recipes = {} # 本当はリストで保存はしないが、都合がよいので辞書型にはしない

        for recipe in self.ingre.items():
            fixed_recipe = {}
            for ingredient in recipe[1].items():
                tmp = self.exchange_mount[self.exchange_amount["name"] == ingredient[0]]
                tmp = tmp[~tmp.duplicated(subset="name")]
                fixed_recipe[str(tmp["id"].tolist()[0])] = ingredient[1]
            fixed_recipes[recipe[0]] = fixed_recipe

        nutrition_list = []

        for recipe in tq(fixed_recipes.items(), total=len(fixed_recipes)):
            
            nutrition = np.arange(30,dtype=float)

            for ingredient in recipe[1].items():
                tmp = self.nutrition[self.nutrition["id"] == float(ingredient[0])]
                nutrition += tmp[["kcal","water","prot",\
                "chole","fat","fib","polyl","na","k","ca","mg","p","fe","zn","cu","mn",\
                    "iodine","se","cr","mo","vitd","vitk","thla","ribf","nia","vitb12","fol",\
                        "pantac","biot","vitc"]].values[0] * ingredient[1] * 0.01

            nutrition_row = []
            nutrition_row.append(recipe[0])

            for digit in nutrition:
                nutrition_row.append(digit)
            nutrition_list.append(nutrition_row)

        recipe_nutrition = pd.DataFrame(nutrition_list, columns=["id","kcal","water","prot",\
            "chole","fat","fib","polyl","na","k","ca","mg","p","fe","zn","cu","mn",\
                "iodine","se","cr","mo","vitd","vitk","thla","ribf","nia","vitb12","fol",\
                    "pantac","biot","vitc"])
        output_path = "../data/recipe_nutrition_" + self.flag + ".csv"
        recipe_nutrition.to_csv(output_path)