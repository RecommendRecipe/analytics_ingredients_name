import json

file = open("../data/scrdata/adult_video.json",'r')
pre_video = json.load(file)
file.close()
clean_video = []

for video in pre_video:
    video["describe"] = video["describe"].replace('\n','')
    tmp = []
    if(len(video["review"])!=0):
        for review in video["review"]:
            tmp.append(review.replace('\n',''))
    else:
        pass
    video["review"] = tmp
    clean_video.append(video)

output_data = json.dumps(clean_video,ensure_ascii=False,indent=2)

with open("../data/scrdata/clean_adult_video.json", "w") as f:
    f.write(output_data)
print("前処理が終了いたしました。")