# htmlソースの取得
import requests
# スクレイピングに使うライブラリ
from bs4 import BeautifulSoup
# リクエストの間隔を開けるため
import time
# 進捗を表示
from tqdm import tqdm as tq
# 最終的にはjson形式で出力
import json

print("urlのリストを読み込んでいます.\n")
f = open('../data/url_list/dmm_url.txt', 'r')
data = f.read()
f.close()
sex_video_urls = data.split(",")
print("総コンテンツ数:",len(sex_video_urls),"\n")

base_url = "https://www.dmm.co.jp"
# 18歳未満かどうかの確認画面をパスするためのurl
check_url = "https://www.dmm.co.jp/age_check/=/declared=yes/?rurl=https%3A%2F%2Fwww.dmm.co.jp%2Ftop%2F"

session = requests.session()
session.get(check_url)

print("データの取得を開始します。")

sex_video_feats = []
error = [] 
for url in tq(sex_video_urls,total=len(sex_video_urls)):
  try:
    sex_video_feat = {} # 作品の特徴量を格納する辞書
    contents = BeautifulSoup(session.get(url).content,features="html.parser")
    sex_video_feat['id'] = contents.find("table",class_="mg-b20").find_all("td")[21].text

    sex_video_feat['title'] = contents.find("h1",id="title").text
    sex_video_feat['base_url'] = url
    sex_video_feat['image'] = contents.find("a",target="_package").get('href')
    sex_video_feat['tag'] = [ tag.text for tag in contents.find_all("a",{'data-i3ref' : 'detail'})]
    sex_video_feat['describe'] = contents.find("div",class_='lh4').text
    review_feat = []
    tmp = contents.find("div",class_="d-review__list")
    if tmp:
      tmp = tmp.find_all("li")
      for review in tmp:
        if review.find("span",class_="d-rating-50"):
          review_feat.append(review.find("div",class_="d-review__unit__comment").text)
        else:
          pass
    else:
      pass

    sex_video_feat["review"] = review_feat
    #print(sex_video_feat)
    sex_video_feats.append(sex_video_feat)
    #time.sleep(1)
  except requests.exceptions.ConnectionError:
    error.append(url)
    time.sleep(600)
  except AttributeError:
    error.append(url)
  except KeyboardInterrupt:
    output = json.dumps(sex_video_feats,ensure_ascii=False,indent=2)
    file = open("../data/scrdata/adult_video.json","w")
    file.write(output)
    file.close()
    exit()
output = json.dumps(sex_video_feats,ensure_ascii=False,indent=2)
file = open("../data/scrdata/adult_video.json","w")
file.write(output)
file.close()
file = open("../data/url_list/adult_video_error.txt","w")
file.write(",".join(error))
file.close()
print("取得が完了しました。")
