import sys
import time
import json
import subprocess
from mahjong_race import run_race


def main_in_subprocess():
    filenames = sys.argv[1].split(";")
    start_seed = int(sys.argv[2])
    end_seed = int(sys.argv[3])

    print(f"subprocess for [{start_seed}, {end_seed})")

    start = time.time()

    race_score = {0: 0, 1: 0, 2: 0, 3: 0}
    score_rank = [4, 3, 2, 1]

    for seed in range(start_seed, end_seed):
        round_id = seed - start_seed + 1
        total_round_count = end_seed - start_seed
        print(f"本进程的第{round_id}/{total_round_count}轮比赛即将开始，种子为{seed}")
        scores = run_race(filenames, seed)
        score_ids = [(i, [j[0] for j in scores.items() if j[1] == i]) for i in sorted(set(scores.values()), reverse=True)]

        rank_id = 0
        for (score, playerids) in score_ids:
            rank = score_rank[rank_id]
            for playerid in playerids:
                race_score[playerid] += rank
            rank_id += 1

    end = time.time()
    print(f"seed: [{start_seed}, {end_seed}) 已完成，耗时{end - start:.3f}秒")
    print("RaceScore::", json.dumps(race_score))
    print("RaceScore::", json.dumps(race_score), file=sys.stderr)


def main():
    if len(sys.argv) >= 2:  # 是子进程
        return main_in_subprocess()
    filenames = [r"D:\Projects\mahjong-versions\v1\__main__.py"]

    round_count = 32
    process_count = 2
    count_per_process = 1 + (round_count - 1) // process_count

    start_seed = 6000
    end_seed = start_seed + round_count

    race_score = {0: 0, 1: 0, 2: 0, 3: 0}
    start = time.time()

    processes = []
    i = start_seed
    while i < end_seed:
        j = i + count_per_process
        if j > end_seed:
            j = end_seed
        filename_str = ';'.join(filenames)
        p = subprocess.Popen(["python", "mahjong_race_parallel.py", filename_str, str(i), str(j)], stderr=subprocess.PIPE)
        processes.append(p)
        i = j

    for p in processes:
        lines = p.stderr.read().decode("utf8").splitlines()
        for line in lines:
            if line.startswith("RaceScore::"):
                score = json.loads(line.removeprefix("RaceScore::"))
                break
        else:
            raise RuntimeError("no score")
        print(score)
        print(race_score)
        for i in race_score:
            race_score[i] += score[str(i)]

    end = time.time()

    print("最终排名：")
    print(race_score)
    print("循环赛耗时：", round(end - start, 3), "秒")

    with open("race_result.json", "w", encoding="utf8") as fs:
        json.dump(race_score, fs, indent=4)

    time.sleep(3)


if __name__ == '__main__':
    main()
