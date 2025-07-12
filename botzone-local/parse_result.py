import json
import ast
import time

filename = "race_result.json"

with open(filename) as fs:
    data = json.load(fs)

race_score = data["race_score"]
round_scores = data["round_scores"]
detail = [ast.literal_eval(i.replace("[[", "(").replace("]]", ")")) for i in data["detail"]]
detail_groups = [detail[j: j+4] for j in range(0, len(detail), 4)]

print(race_score)

获胜局数 = len([i for i in round_scores if i == [4, 3, 3, 3]])
落败局数 = len([i for i in round_scores if i == [3, 4, 4, 4]])
打平局数 = len([i for i in round_scores if i == [4, 4, 4, 4]])

print(f"{获胜局数=} {落败局数=} {打平局数=}")

zimolist = [i for i in detail if all(abs(k[1]) >= 16 for k in i)]  # 自摸时，三家减至少16分，一家获得至少48分
huangzhuanglist = [i for i in detail if all(k[1] == 0 for k in i)]  # 荒庄时，每家都得0分
hupailist = [i for i in detail if len([k for k in i if k[1] == -8]) == 2]  # 点炮时，两家减8分，一家减8+店铺分，一家获得所有分

自摸总收益 = sum(max(i, key=lambda x:x[1])[1] for i in zimolist)
胡牌总收益 = sum(max(i, key=lambda x:x[1])[1] for i in hupailist)

自摸次数 = len(zimolist)  # 自摸时，三家减至少16分，一家获得至少48分
荒庄次数 = len(huangzhuanglist)  # 荒庄时，每家都得0分
胡牌次数 = len(hupailist)  # 点炮时，两家减8分，一家减8+店铺分，一家获得所有分

自摸平均收益 = 自摸总收益 / 自摸次数
胡牌平均收益 = 胡牌总收益 / 胡牌次数

print(f"{自摸次数=} {荒庄次数=} {胡牌次数=}")
print(f"{自摸总收益=} {胡牌总收益=}")
print(f"{自摸平均收益=} {胡牌平均收益=}")

fandict = {}

for i in zimolist:
    fan = max(i, key=lambda x:x[1])[1] // 3 - 8
    fandict.setdefault(fan, 0)
    fandict[fan] += 1

fanlist = sorted(fandict.items(), key=lambda x: x[0])

print(f"自摸牌大小统计：{fanlist}")

fandict = {}

for i in hupailist:
    fan = max(i, key=lambda x:x[1])[1] - 24
    fandict.setdefault(fan, 0)
    fandict[fan] += 1

fanlist = sorted(fandict.items(), key=lambda x: x[0])

print(f"点炮牌大小统计：{fanlist}")

fandict = {}

for i in zimolist:
    fan = max(i, key=lambda x:x[1])[1] // 3 - 8
    fandict.setdefault(fan, 0)
    fandict[fan] += 1

for i in hupailist:
    fan = max(i, key=lambda x:x[1])[1] - 24
    fandict.setdefault(fan, 0)
    fandict[fan] += 1

fanlist = sorted(fandict.items(), key=lambda x: x[0])

print(f"所有牌大小统计：{fanlist}")


