from distutils.log import error
from tqdm import tqdm as tq
from bs4 import BeautifulSoup
import requests
import json
import time

f = open('../data/url_list/rakuten_url_untaken.txt', 'r')
data = f.read()
recipe_url_list = data.split(",")
recipe_list = []
base_url = "https://recipe.rakuten.co.jp"
error = []

def get_para(content):
  if content == None:
    return ""
  else:
    return content.text

for menu in tq(recipe_url_list,total=len(recipe_url_list)):
  recipe = {}
  url = base_url + menu
  try:
    data = BeautifulSoup(requests.get(url,timeout=(3.0,10.0)).content,"html.parser")
    recipe["title"] = get_para(data.find("h1",class_="page_title__text"))
    # 所要時間
    recipe["time"] = get_para(data.find("li",class_="recipe_info__time"))
    # 予算
    recipe["cost"] = get_para(data.find("li",class_="recipe_info__cost"))
    recipe["comment"] = get_para(data.find("div",class_="recipe_info_user__comment"))
    recipe["serving_for"] = get_para(data.find("h2",class_="contents_title_mb"))
    recipe["ingredients"] = [{"name":ingre.find("span",class_="recipe_material__item_name").text,"amount":ingre.find("span",class_="recipe_material__item_serving").text} for ingre in data.find_all("li",class_="recipe_material__item")]
    recipe["step"] = [ step.text for step in data.find_all("span",class_="recipe_howto__text")]
    recipe["sub_comment"] = get_para(data.find("p",class_="recipe_note__trigger_text"))
    # 料理のコツ
    recipe["hint"] = get_para(data.find("p",class_="recipe_note__tips_text"))
    recipe["id"] = get_para(data.find("li",class_="recipe_note__id"))
    # カテゴリと料理タイプ
    tmp = data.find_all("dd",class_="relation_info__item")
    if len(tmp) >= 1:
      recipe["category"] = tmp[0].text
    else:
      recipe["category"] = ""
    if len(tmp) >= 2:
      recipe["type"] = tmp[1].text
    else:
      recipe["type"] = ""

    recipe_list.append(recipe)
  except requests.exceptions.ConnectionError:
    error.append(url)
    time.sleep(600)
  except AttributeError:
    error.append(url)

output_data = json.dumps(recipe_list,ensure_ascii=False,indent=2)
output = open("../data/train_data/rakuten_json/output_rakuten_12.json",'w',encoding='utf-8')
output.write(output_data)
output.close()
