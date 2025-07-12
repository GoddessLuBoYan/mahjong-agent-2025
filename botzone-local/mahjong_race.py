import itertools
import json
import os.path
import random
import subprocess
import sys
import time

from botzone.envs.botzone.chinesestandardmahjong import ChineseStandardMahjongEnv
from mybot import MyBot, MyBotFromPool


def create_initdata(seed):
    r = random.Random(seed)
    quan = r.randint(0, 3)
    srand = seed
    tilelist = [f"{i}{j}" for _ in range(4) for (i, k) in ["W9", "B9", "T9", "F4", "J3"] for j in range(1, int(k) + 1)]
    assert len(tilelist) == 136, len(tilelist)
    r.shuffle(tilelist)
    return {
        "quan": quan,
        "srand": srand,
        "walltiles": " ".join(tilelist)
    }


def create_bot(filename):
    dirname = os.path.dirname(filename)
    #print(f"create bot from {dirname=} {filename=}")
    return MyBotFromPool(dirname, filename)


def run_one_round(filename_list, seed):
    initdata = create_initdata(seed)
    env = ChineseStandardMahjongEnv(duplicate=True)

    bots = [create_bot(filename) for filename in filename_list]

    try:
        # 指定对局玩家
        env.init(bots)
        # 运行对局并渲染画面
        score = env.reset(initdata=initdata)
        #env.render()
        while score is None:
            score = env.step()  # 对局结束时，step会以tuple的形式返回各玩家得分
    except:
        import traceback
        traceback.print_exc()
    finally:
        for bot in bots:
            try:
                bot.close()
            except:
                pass

    return score


def run_race(filename_list: list, seed):
    #return {0: 32, 1: -16, 2: -8, 3: -8}
    baseline_filename = BASELINE_FILENAME
    assert len(filename_list) <= 4
    flist = list(filename_list)
    iddict = {filename: i for i, filename in enumerate(flist)}
    while len(flist) < 4:
        flist.append(baseline_filename)

    scores = {i: 0 for i in range(4)}
    runned_dict = {}

    result_list = []
    for seats in itertools.permutations(range(4)):
        filenames = tuple(flist[i] for i in seats)
        if filenames in runned_dict:
            score = runned_dict[filenames]
        else:
            score = runned_dict[filenames] = run_one_round(filenames, seed)
            # id为0的玩家用双中括号括起来，其他玩家用小括号括起来
            print(*[tuple(item) if item[0] != 0 else [list(item)] for item in zip(seats, score)], sep=", ")

        result = sorted(zip(seats, score))
        result_list.append((seats, result))
        for (i, s) in result:
            scores[i] += s
    return scores


BASELINE_FILENAME = r"C:\MyProjects\ProgramProjects\66848fb9b54d400b709c4424\__main__.py"


def main():
    filenames = [
        r"D:\Projects\mahjong-versions\v4\__main__.py",
        r"D:\Projects\mahjong-versions\v1\__main__.py",
        r"D:\Projects\mahjong-versions\v1\__main__.py",
        r"D:\Projects\mahjong-versions\v1\__main__.py",
    ]

    start_seed = 6000
    round_count = 1

    start = time.time()

    race_score = {0: 0, 1: 0, 2: 0, 3: 0}
    score_rank = [4, 3, 2, 1]

    for round_id in range(1, round_count + 1):
        seed = start_seed + round_id - 1
        print(f"第{round_id}轮比赛即将开始，种子为{seed}")
        scores = run_race(filenames, seed)
        print(f"本轮比赛结果: {scores}")
        print("当前耗时：", round(time.time() - start, 3), "秒")
        score_ids = [(i, [j[0] for j in scores.items() if j[1] == i]) for i in sorted(set(scores.values()), reverse=True)]

        rank_id = 0
        for (score, playerids) in score_ids:
            rank = score_rank[rank_id]
            for playerid in playerids:
                race_score[playerid] += rank
            rank_id += 1

    end = time.time()

    print("最终排名：")
    print(race_score)
    print("循环赛耗时：", round(end - start, 3), "秒")
    time.sleep(3)


if __name__ == '__main__':
    main()




