import requests
# スクレイピングに使うライブラリ
from bs4 import BeautifulSoup
from tqdm import tqdm

# 取得するurlを格納するリスト
colum_urls = []
base_url = "https://recipe.rakuten.co.jp"
url = base_url + "/category/"


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
  data = BeautifulSoup(requests.get(url).content,"html.parser")
  tmp_lists = [tmp.get("href") for tmp in data.find_all("a",class_="recipe_ranking__link")]
  recipe_url_lists += tmp_lists
  
  # 次のページ内のurlを取得
  page_num += 1
  next_url = base_url + menu + str(page_num) + "/" + pack
  data = BeautifulSoup(requests.get(next_url).content,"html.parser")
  cap_john = data.find_all("a",class_="recipe_ranking__link")
  
  exist = True
  while exist:
    # urlの格納
    tmp_lists = [tmp.get("href") for tmp in cap_john]
    recipe_url_lists += tmp_lists

    # 次のページ内のurlの取得
    page_num += 1
    next_url = base_url + menu + str(page_num) + "/" + pack
    # 固まらないようにたいむあうとを設定
    try:
      data = BeautifulSoup(requests.get(next_url,timeout=(6.0,10)).content,"html.parser")
      cap_john = data.find_all("a",class_="recipe_ranking__link")
      if len(cap_john) == 0 :
        exist = False
        page_num = 1
    except:
      pass

recipe_url_lists = list(set(recipe_url_lists))
print(len(recipe_url_lists))

with open("../data/url_list/rakuten_url_tmp.txt","w") as f:
  f.write(",".join(recipe_url_lists))


# 既存のurlリストを参照
"""
with open("../data/url_list/rakuten_url.txt","r") as f:
    old_list = f.read().split(',')
print("取得済みのパス:",len(old_list))
with open("../data/url_list/rakuten_url_untaken.txt","w") as f:
    update_list = [url for url in recipe_url_lists if url not in old_list]
    print("新規で見つかったパスの数:",len(update_list))
    f.write(",".join(update_list))

"""