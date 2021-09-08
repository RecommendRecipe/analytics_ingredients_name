# htmlソースの取得
import requests
# スクレイピングに使うライブラリ
from bs4 import BeautifulSoup

from tqdm import tqdm as tq

# 取得するurlを格納するリスト
sex_act_urls = []

base_url = "https://www.dmm.co.jp"
url = "https://www.dmm.co.jp/digital/videoa/-/actress/=/keyword=a/"
check_url = "https://www.dmm.co.jp/age_check/=/declared=yes/?rurl=https%3A%2F%2Fwww.dmm.co.jp%2Ftop%2F"

session = requests.session()
session.get(check_url)
data = session.get(url)
aiueo_list = []

tmp = BeautifulSoup(data.content,"html.parser")
tmp = tmp.find("ul",class_="d-item").find_all("a")
aiueo_list = [ urls.get('href') for urls in tmp]
aiueo_list.append("/digital/videoa/-/actress/=/keyword=a/")

for actress in aiueo_list:
  
  i = 1
  check = True
  while check:
    act_url = actress + "page=" + str(i) + "/"
    data = session.get(base_url + act_url)
    contents = BeautifulSoup(data.content,"html.parser")
    tmp = contents.find('ul',class_="act-box-100")
    tmp = tmp.find_all('a')
    if len(tmp) > 0:
      # aタグの中のurlを取得
      urls = [url.get('href') for url in tmp ]
      # 取得したurlを追加
      sex_act_urls += urls
      i += 1
    else:
      check = False
      break

print("女優の数")
print(len(sex_act_urls))

# AVのURLを入手

sex_video_url = []
for act_url in tq(sex_act_urls,total=len(sex_act_urls)):
  i = 1
  check = True
  while check:
    tmp_url = act_url
    
    if i != 1:
      tmp_url = act_url + "page=" + str(i) + "/"
    try:
        data = session.get(tmp_url,timeout=(6.0,10))
    except:
        break
    if data.url != tmp_url:
      check = False
      break
    else:
      contents = BeautifulSoup(data.content,"html.parser")
      tmp = contents.find_all("p",class_="tmb")
      # aタグの中のurlを取得
      urls = [url.find("a").get('href') for url in tmp ]
      # 取得したurlを追加
      sex_video_url += urls
      i += 1

file = open("../data/dmm_url.txt",mode='w',encoding='utf-8')
file.write(",".join(sex_video_url))
file.close()

print(len(sex_video_url))