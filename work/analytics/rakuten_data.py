from tqdm.notebook import tqdm_notebook as tq
from bs4 import BeautifulSoup
import requests

f = open('../data/sep_scry_data/rakuten-url1.txt', 'r')
data = f.read()
recipe_url_list = data.split(",")
recipe_list = []
base_url = "https://recipe.rakuten.co.jp"

for menu in tq(recipe_url_list,total=len(recipe_url_list)):
  recipe = {}
  url = base_url + menu
  data = BeautifulSoup(requests.get(url).content,"html.parser")
  
  recipe["title"] = data.find("h1",class_="page_title__text").text
  # 所要時間
  tmp = data.find("li",class_="recipe_info__time")
  if tmp != None:
    recipe["time"] = tmp.text
  else:
    recipe["time"] = ""
  # 予算
  tmp = data.find("li",class_="recipe_info__cost")
  if tmp != None:
    recipe["cost"] = tmp.text
  else:
    recipe["cost"] = ""
  recipe["comment"] = data.find("div",class_="recipe_info_user__comment").text
  recipe["serving_for"] = data.find("h2",class_="contents_title_mb").text
  recipe["ingredients"] = [{"name":ingre.find("span",class_="recipe_material__item_name").text,"amount":ingre.find("span",class_="recipe_material__item_serving").text} for ingre in data.find_all("li",class_="recipe_material__item")]
  recipe["step"] = [ step.text for step in data.find_all("span",class_="recipe_howto__text")]
  recipe["sub_comment"] = data.find("p",class_="recipe_note__trigger_text").text
  # 料理のコツ
  tmp = data.find("p",class_="recipe_note__tips_text")
  if tmp != None:
    recipe["hint"] = tmp.text
  else:
    recipe["hint"] = ""
  recipe["id"] = data.find("li",class_="recipe_note__id").text[6:]
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

print(len(recipe_list))