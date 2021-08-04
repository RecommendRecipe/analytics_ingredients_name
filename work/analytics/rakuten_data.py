import requests
# スクレイピングに使うライブラリ
from bs4 import BeautifulSoup
from tqdm import tqdm

# 取得するurlを格納するリスト
colum_urls = []
base_url = "https://recipe.rakuten.co.jp"
url = base_url + "/category/"
#pack ="&sort=new"

session = requests.session()
session.get(base_url)
data = session.get(url)
data = BeautifulSoup(data.content,"html.parser")

top_link = data.find_all("a",class_="category_top-list__link")
small_list_link = data.find_all("a",class_="category_top-smallList__link")
url_list = [ingre.get("href") for ingre in top_link]
url_list += [ingre.get("href") for ingre in small_list_link]


recipe_url_lists= []
i = 0
page_num = 1
pack = "?s=0"
# csvとして保存する為にそれぞれリストで格納
for menu in tqdm(url_list,total=len(url_list)):
  # 初めのindexページの処理
  url = base_url + menu + pack
  data = BeautifulSoup(session.get(url).content,"html.parser")
  tmp_lists = [tmp.get("href") for tmp in data.find_all("a",class_="recipe_ranking__link")]
  recipe_url_lists += tmp_lists
  
  # 次のページ内のurlを取得
  page_num += 1
  next_url = base_url + menu + str(page_num) + "/" + pack
  data = BeautifulSoup(session.get(next_url).content,"html.parser")
  cap_john = data.find_all("a",class_="recipe_ranking__link")
  
  exist = True
  while exist:
    # urlの格納
    tmp_lists = [tmp.get("href") for tmp in cap_john]
    recipe_url_lists += tmp_lists

    # 次のページ内のurlの取得
    page_num += 1
    next_url = base_url + menu + str(page_num) + "/" + pack
    data = BeautifulSoup(session.get(next_url).content,"html.parser")
    cap_john = data.find_all("a",class_="recipe_ranking__link")
    if len(cap_john) == 0 :
      exist = False
      page_num = 1

print(len(recipe_url_lists))
recipe_url_lists = list(set(recipe_url_lists))
print(len(recipe_url_lists))
file = open("../data/rakuten_url.txt",mode='w',encoding='utf-8')
file.write(",".join(recipe_url_lists))
file.close()