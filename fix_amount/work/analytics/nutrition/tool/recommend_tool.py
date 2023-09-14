import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math

def sim(nutrition_list,ingredients_list: dict,user_nutrition,user_ingredient: dict) -> int:
    
    # 栄養素ベクトルとの類似度の算出
    nutrition_sim = cosine_similarity([user_nutrition], nutrition_list)

    # 食材ベクトルとの類似度の算出
    ingredients_sim = []

    for recipe in ingredients_list.items():
        
        match_ingre_list = []
        innor_pro = 0
        search_vec_distance = 0
        content_vec_distance = 0

        for ingredient in recipe[1].items():
            
            if ingredient[0] in user_ingredient:
                search_vec_distance += user_ingredient[ingredient[0]] ** 2
                content_vec_distance += ingredient[1] ** 2
                match_ingre_list.append(ingredient[0])
                innor_pro += ingredient[1] * user_ingredient[ingredient[0]]
        
        if len(match_ingre_list) == 0:
            ingredients_sim.append(0.0)
        else:
            ingredients_sim.append(innor_pro/ (math.sqrt(search_vec_distance) * math.sqrt(content_vec_distance) ))

    return np.argmax(nutrition_sim * ingredients_sim)