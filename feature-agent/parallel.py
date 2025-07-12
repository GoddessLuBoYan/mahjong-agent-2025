#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author  :   Arthals
# @File    :   parallel.py
# @Time    :   2024/06/30 18:42:55
# @Contact :   zhuozhiyongde@126.com
# @Software:   Visual Studio Code

"""
parallel.py: 并行处理数据，将数据分成多个进程处理，加快处理速度。
"""

import json
import multiprocessing
import os
import math


def find_match_lines(file_path):
    match_lines = []
    total_lines = -1
    with open(file_path, "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            if line.startswith("Match"):
                match_lines.append(i)
            total_lines = i
    total_lines += 1
    return match_lines, total_lines


def parallel_process(file_path, start_line, end_line, offset, cpu_id, output_dir, match_per_process):
    os.system(
        f"python preprocess.py {file_path} {start_line} {end_line} {offset} {cpu_id} {output_dir} {match_per_process}"
    )


if __name__ == "__main__":
    file_name = r"./data"
    output_dir = r"./data-vec"

    os.makedirs(output_dir, exist_ok=True)
    file_path = f"{file_name}/sample.txt"

    match_lines, total_lines = find_match_lines(file_path)
    total_matches = len(match_lines)
    print(len(match_lines), total_lines)

    num_cpus = multiprocessing.cpu_count()
    if len(match_lines) <= 20:
        num_cpus = 1
        
    match_per_process = math.ceil(len(match_lines)/num_cpus)
    chunk_size = num_cpus * match_per_process  # 每个进程处理 match_per_process 场比赛

    processes = []
    total_chunks = len(match_lines) // chunk_size + (
        1 if len(match_lines) % chunk_size != 0 else 0
    )

    for chunk_id in range(total_chunks):
        start_index = chunk_id * chunk_size

        for i in range(num_cpus):
            if start_index + i * match_per_process >= total_matches:
                break
            start_line = match_lines[start_index + i * match_per_process]
            end_line = (
                match_lines[start_index + (i + 1) * match_per_process] - 1
                if (start_index + (i + 1) * match_per_process) < total_matches
                else total_lines
            )

            offset = start_index + i * match_per_process

            cpu_id = chunk_id * num_cpus + i
            p = multiprocessing.Process(
                target=parallel_process,
                args=(
                    file_path,
                    start_line,
                    end_line,
                    offset,
                    cpu_id,
                    output_dir,
                    match_per_process
                ),
            )
            processes.append((cpu_id, p))
            p.start()

        for cpu_id, p in processes:
            p.join()
            print(f"进程{cpu_id}已完成")
        processes.clear()  # 清除进程列表，准备下一轮

    # 合并所有进程生成的 JSON 文件
    total_out = []
    for chunk_id in range(total_chunks):
        for i in range(num_cpus):
            try:
                with open(
                    f"{output_dir}/count-{chunk_id * num_cpus + i}.json", "r"
                ) as f:
                    total_out += json.load(f)
                    # os.remove(f"{output_dir}/count-{chunk_id * num_cpus + i}.json")
            except FileNotFoundError:
                continue

    with open(f"{output_dir}/count.json", "w") as f:
        json.dump(total_out, f)

    # 校验 count.json 和 data-count-back.json 是否一致
    # count = total_out

    # with open(f"{output_dir}/data-count-back.json", "r") as f:
    #     count_backup = json.load(f)

    # print(len(count), len(count_backup))

    # # 检查是否一致
    # for i in range(len(count)):
    #     if count[i] != count_backup[i]:
    #         print(i)
    #         print(count[i], count_backup[i])
    #         break
