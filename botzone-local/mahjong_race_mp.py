import sys
import time
import json
import subprocess
import itertools
from dataclasses import dataclass
from typing import Any
import io
from queue import Empty
from multiprocessing import Queue, Process
from mahjong_race import run_one_round, BASELINE_FILENAME


@dataclass
class Item:
    round_id: int = -1
    args: Any = None
    ret: Any = None


def run_race(filename_list: list, seed):
    #return {0: 32, 1: -16, 2: -8, 3: -8}
    baseline_filename = BASELINE_FILENAME
    assert len(filename_list) <= 4
    flist = list(filename_list)

    while len(flist) < 4:
        flist.append(baseline_filename)

    scores = {i: 0 for i in range(4)}
    runned_dict = {}
    print_strs = []

    result_list = []
    for seats in itertools.permutations(range(4)):
        filenames = tuple(flist[i] for i in seats)
        if filenames in runned_dict:
            score = runned_dict[filenames]
        else:
            score = runned_dict[filenames] = run_one_round(filenames, seed)
            # id为0的玩家用双中括号括起来，其他玩家用小括号括起来
            buffer = io.StringIO()
            print(*[tuple(item) if item[0] != 0 else [list(item)] for item in zip(seats, score)], sep=", ", file=buffer)
            buffer.seek(0)
            print_str = buffer.getvalue()
            print_strs.append(print_str)

        result = sorted(zip(seats, score))
        result_list.append((seats, result))
        for (i, s) in result:
            scores[i] += s
    return scores, print_strs


def calc_race_score(scores):

    race_score = {0: 0, 1: 0, 2: 0, 3: 0}
    score_rank = [4, 3, 2, 1]
    score_ids = [(i, [j[0] for j in scores.items() if j[1] == i]) for i in sorted(set(scores.values()), reverse=True)]

    rank_id = 0
    for (score, playerids) in score_ids:
        rank = score_rank[rank_id]
        for playerid in playerids:
            race_score[playerid] += rank
        rank_id += 1

    return race_score


def worker(worker_id: int, input_q: Queue, output_q: Queue):
    print(f"工作进程{worker_id}已启动")
    time.sleep(worker_id * 4)  # 工作进程依次启动，防止所有进程同时初始化导致实例化Bot超时失败
    while True:
        item: Item = input_q.get()
        if item.round_id < 0:
            break
        ret = run_race(*item.args)
        item.ret = ret
        output_q.put(item)
    print(f"工作进程{worker_id}已完成")


def main():
    filenames = [
        r"D:\Projects\mahjong-versions\v1_hufix\__main__.py",
        r"D:\Projects\mahjong-versions\v1\__main__.py",
        r"D:\Projects\mahjong-versions\v1\__main__.py",
        r"D:\Projects\mahjong-versions\v1\__main__.py",
    ]

    round_count = 256
    process_count = 4

    start_seed = 6000
    end_seed = start_seed + round_count

    race_score = {0: 0, 1: 0, 2: 0, 3: 0}
    start = time.time()

    input_q = Queue()
    output_q = Queue()

    processes = []
    for i in range(process_count):
        p = Process(target=worker, args=(i, input_q, output_q))
        p.start()
        processes.append(p)

    input_items = []

    for round_id in range(1, round_count + 1):
        seed = start_seed + round_id - 1
        item = Item(round_id=round_id, args=(filenames, seed))
        input_q.put(item)
        input_items.append(item)
    print(f"所有比赛(共{round_count}轮)已进入队列，等待结束中")

    round_id = 1
    output_items = {}

    round_score_list = []
    detail_list = []

    while round_id <= round_count:
        try:
            item = output_q.get(timeout=1.)
        except Empty:
            continue
        output_items[item.round_id] = item

        while True:
            if round_id not in output_items:
                break
            round_item: Item = output_items[round_id]
            scores, print_strs = round_item.ret

            print(f"====== 第{round_id}轮比赛成绩表 ======")

            for print_str in print_strs:
                print(print_str)
                detail_list.append(print_str)

            round_score = calc_race_score(scores)
            round_score_list.append([round_score[k] for k in range(4)])
            for i in race_score:
                race_score[i] += round_score[i]

            print("本轮成绩: ", scores)
            print("本轮排名: ", round_score)
            print("当前总排名: ", race_score)
            print("当前耗时：", round(time.time() - start, 3), "秒")

            print(f"====== 第{round_id}轮比赛已完成 ======")
            print()
            print()

            round_id += 1

    end = time.time()

    print("最终排名：")
    print(race_score)
    print("循环赛耗时：", round(end - start, 3), "秒")

    for i in range(process_count):
        input_q.put(Item(round_id=-1))

    save_result = {
        "race_score": race_score,
        "round_scores": round_score_list,
        "detail": detail_list,
    }

    with open(f"race_result_{int(time.time() * 1000)}.json", "w", encoding="utf8") as fs:
        json.dump(save_result, fs, indent=4)

    time.sleep(3)


if __name__ == '__main__':
    main()
