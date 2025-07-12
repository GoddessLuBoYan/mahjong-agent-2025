


import time
import itertools
import numpy as np
import faiss
import pickle
import functools
from enum import Enum
from typing import Tuple, Dict


FAN = {
    '大四喜': 88,
    '大三元': 88,
    '绿一色': 88,
    '九莲宝灯': 88,
    '四杠': 88,
    '连七对': 88,
    '十三幺': 88,
    '清幺九': 64,
    '小四喜': 64,
    '小三元': 64,
    '字一色': 64,
    '四暗刻': 64,
    '一色双龙会': 64,
    '一色四同顺': 48,
    '一色四节高': 48,
    '一色四步高': 32,
    '三杠': 32,
    '混幺九': 32,
    '七对': 24,
    '七星不靠': 24,
    '组合不靠': 24,
    '全双刻': 24,
    '清一色': 24,
    '一色三同顺': 24,
    '一色三节高': 24,
    '全大': 24,
    '全中': 24,
    '全小': 24,
    '清龙': 16,
    '三色双龙会': 16,
    '一色三步高': 16,
    '全带五': 16,
    '三同刻': 16,
    '三暗刻': 16,
    '全不靠': 12,
    '组合龙': 12,
    '大于五': 12,
    '小于五': 12,
    '三风刻': 12,
    '花龙': 8,
    '推不倒': 8,
    '三色三同顺': 8,
    '三色三节高': 8,
    '无番和': 8,
    '妙手回春': 8,
    '海底捞月': 8,
    '杠上开花': 8,
    '抢杠和': 8,
    '碰碰和': 6,
    '混一色': 6,
    '三色三步高': 6,
    '五门齐': 6,
    '全求人': 6,
    '双暗杠': 6,
    '双箭刻': 6,
    '明暗杠': 5,
    '全带幺': 4,
    '不求人': 4,
    '双明杠': 4,
    '和绝张': 4,
    '箭刻': 2,
    '圈风刻': 2,
    '门风刻': 2,
    '门前清': 2,
    '平和': 2,
    '四归一': 2,
    '双同刻': 2,
    '双暗刻': 2,
    '暗杠': 2,
    '断幺': 2,
    '一般高': 1,
    '喜相逢': 1,
    '连六': 1,
    '老少副': 1,
    '幺九刻': 1,
    '明杠': 1,
    '缺一门': 1,
    '无字': 1,
    '边张': 1,
    '坎张': 1,
    '单钓将': 1,
    '自摸': 1,
    '花牌': 1,
    '荒庄': 0,
    '零碎番': 0
 }
FAN_NAMES = ['大四喜', '大三元', '绿一色', '九莲宝灯', '四杠', '连七对', '十三幺', '清幺九', '小四喜', '小三元', '字一色', '四暗刻', '一色双龙会', '一色四同顺', '一色四节高', '一色四步高', '三杠', 
             '混幺九', '七对', '七星不靠', '组合不靠', '全双刻', '清一色', '一色三同顺', '一色三节高', '全大', '全中', '全小', '清龙', '三色双龙会', '一色三步高', '全带五', '三同刻', '三暗刻', '全不靠', '组合龙', 
             '大于五', '小于五', '三风刻', '花龙', '推不倒', '三色三同顺', '三色三节高', '无番和', '妙手回春', '海底捞月', '杠上开花', '抢杠和', '碰碰和', '混一色', '三色三步高', '五门齐', '全求人', 
             '双暗杠', '双箭刻', '明暗杠', '全带幺', '不求人', '双明杠', '和绝张', '箭刻', '圈风刻', '门风刻', '门前清', '平和', '四归一', '双同刻', '双暗刻', '暗杠', '断幺', '一般高', '喜相逢', '连六', 
             '老少副', '幺九刻', '明杠', '缺一门', '无字', '边张', '坎张', '单钓将', '自摸', '花牌', '荒庄', '零碎番']

TILE_LIST = [
    *("W%d" % (i + 1) for i in range(9)),  # 万
    *("T%d" % (i + 1) for i in range(9)),  # 条
    *("B%d" % (i + 1) for i in range(9)),  # 饼
    *("F%d" % (i + 1) for i in range(4)),  # 风
    *("J%d" % (i + 1) for i in range(3)),  # 箭
]
OFFSET_TILE = {c: i for i, c in enumerate(TILE_LIST)}
OFFSET_TILE["CONCEALED"] = 34

class OffsetPoint:
    NAME_ID = 0  # +1
    HAND_COUNT = 1  # +1
    TILE_COUNT = 2  # +34
    PACK_TYPE = 36  # +1
    TILES = 37  # +14

    LENGTH = 51


class PackType:
    NONE = 0
    TOTAL = 1  # 只有一组牌，整体型
    BASIC = 2  # 有2~5组牌，基本型
    BASIC_WITH_PAIR = 3  # 有2~5组牌，基本型
    QIDUI = 4  # 有7组牌，七对型


def get_xianten_once(packs: Tuple[Tuple[str]], hand: Tuple[str], wanted_packs: Tuple[Tuple[str]]):
    """
    先遍历pack，剔除已有的packs
    再遍历hand，将手牌组成pack，组不成pack的需要明确可以通过什么行为获取（抓、吃、碰、杠）
    
    为方便起见，我们假设packs中，杠和碰等效，且格式为(tile, tile, tile)而不是(type, tile, num)
    """

    rest_packs = list(wanted_packs)
    for pack in packs:
        if pack in rest_packs:
            rest_packs.remove(pack)
    
    rest_tiles = []
    for pack in rest_packs:
        rest_tiles.extend(pack)

    rest_hand = list(hand)

    for tile in hand:
        if tile in rest_tiles:
            rest_hand.remove(tile)
            rest_tiles.remove(tile)

    get_tile_way_dict = {}

    for pack in rest_packs:
        if len(pack) >= 9:  # 整体型
            continue
        elif len(pack) == 3 and pack[0] == pack[1]:  # 碰
            info = "Peng"
        elif len(pack) == 3 and pack[0] != pack[1]:  # 吃
            info = "Chi"
        elif len(pack) == 2 and pack[0] == pack[1]:  # 雀头
            continue
        else:  # 不合法的情况
            continue
        for tile in pack:
            get_tile_way_dict.setdefault(tile, set()).add(info)

    rest_tiles_with_info = [
        (tile,
        "Chi" in get_tile_way_dict.get(tile, set()), 
        "Peng" in get_tile_way_dict.get(tile, set())) 
    for tile in rest_tiles]

    return rest_tiles_with_info, rest_hand


def hand_to_point(hand):
    hand_point = np.zeros((36,), dtype=np.int8)
    for i in range(34):
        hand_point[2 + i] = hand.count(TILE_LIST[i])
    return hand_point


def get_xianten_all(faiss_instance, packs, hand, topk=5, if_no_angang=True):
    hand_point = hand_to_point(hand)
    
    neighbor_point_infos = faiss_instance.search(hand_point)

    res_list = []
    for point_id in neighbor_point_infos:
        point = faiss_instance.p_hu_array[point_id]
        fan_name = FAN_NAMES[point[OffsetPoint.NAME_ID]]
        if not if_no_angang and fan_name == '无番和':
            continue
        pack_type = point[OffsetPoint.PACK_TYPE]
        tiles = []
        for tile_id in point[OffsetPoint.TILES: OffsetPoint.TILES + 14]:
            if tile_id == -1:
                break
            tiles.append(TILE_LIST[tile_id])
        if pack_type == PackType.TOTAL:
            wanted_packs = (tuple(tiles),)
        elif pack_type == PackType.BASIC:
            assert len(tiles) % 3 == 0
            wanted_packs = tuple([tuple(tiles[i: i+3]) for i in range(0, len(tiles), 3)])
        elif pack_type == PackType.BASIC_WITH_PAIR:
            assert len(tiles) % 3 == 2
            wanted_packs = (tuple(tiles[0: 2]),) + tuple([tuple(tiles[i: i+3]) for i in range(2, len(tiles), 3)])
        elif pack_type == PackType.QIDUI:
            assert len(tiles) == 14
            wanted_packs = tuple([tiles[i:i + 2] for i in range(0, len(tiles), 2)])

        fan_value = FAN[fan_name]
        res = get_xianten_once(packs, hand, wanted_packs)
        if res:
            res_list.append((fan_name, fan_value, res))
        if len(res_list) >= topk:
            break
    return res_list


def get_xianten_all_by_instance_dict(faiss_instance_dict, packs, hand, topk=5, if_no_angang=True):
    # 首先对频率特别高的番做过滤。注意手牌可能13张也可能14张
    is_self_play = len(hand) % 3 == 2  # 14张说明需要自己打出一张，13张说明自己不需要打出，可能只是需要吃碰杠
    hand_point = hand_to_point(hand)
    hand_types_set = set(i[0] for i in hand)
    important_fan_names = ['五门齐', '混一色', '全带幺', '清一色', '无番和', '大于五', '小于五', '推不倒']
    important_fan_name_avaliable = [False] * len(important_fan_names)
    # 五门齐
    # 如果只有3类牌，说明向听数至少为5，剩下两类需要组一个3张一个2张，几乎不可能。此时一般倾向于做三色三步高或者缺门
    important_fan_name_avaliable[0] = len(set(i[0] for i in hand)) <= 3
    # 混一色
    # 如果WBT中，任意两种花色的牌加起来不小于5，说明向听数至少为5，几乎不可能。此外，如果没有字牌，则直接拟合清一色即可
    important_fan_name_avaliable[1] = min([sum(1 for i in hand if i[0] in t) for t in ["WB", "BT", "WT"]]) < 5 and ("F" in hand_types_set or "J" in hand_types_set)
    # 全带幺
    # 如果4、5、6的牌加起来数量不小于5，说明向听数至少为5，几乎不可能
    important_fan_name_avaliable[2] = sum(1 for i in hand if i[0] in "WBT" and i[1] in "456") < 5
    # 清一色
    # 如果WBT中，任意一种花色以外的牌数量都不少于5，说明向听数至少为5，几乎不可能
    important_fan_name_avaliable[3] = min([sum(1 for i in hand if i[0] in t) for t in ["WBFJ", "BTFJ", "WTFJ"]]) < 5
    # 无番和
    # 如果有暗杠一定不成立；风将都没有且缺门则向听数至少为4（缺门摸2张，风将抓个对子），几乎不可能
    important_fan_name_avaliable[4] = if_no_angang and len(hand_types_set) >= 3
    # 大于五
    # 如果不符合条件的牌不少于5张则几乎不可能
    important_fan_name_avaliable[5] = sum(1 for i in hand if i[0] not in "WBT" or i[1] not in "6789") < 5
    # 小于五
    # 如果不符合条件的牌不少于5张则几乎不可能
    important_fan_name_avaliable[6] = sum(1 for i in hand if i[0] not in "WBT" or i[1] not in "1234") < 5
    # 推不倒
    # 如果不符合条件的牌不少于5张则几乎不可能
    important_fan_name_avaliable[7] = sum(1 for i in hand if i not in "B1 B2 B3 B4 B5 B8 B9 T2 T4 T5 T6 T8 T9 J3".split(" ")) < 5
    neighbor_point_infos = []
    for fan_name, avaliable in zip(important_fan_names, important_fan_name_avaliable):
        if not avaliable:
            continue
        for point_id, distance in faiss_instance_dict[fan_name].search_return_distance(hand_point, topk):
            neighbor_point_infos.append((fan_name, point_id, distance))
    for point_id, distance in faiss_instance_dict["others"].search_return_distance(hand_point, topk):
        neighbor_point_infos.append(("others", point_id, distance))
    neighbor_point_infos.sort(key=lambda x:x[2])
    res_list = []
    for fan_name, point_id, distance in neighbor_point_infos[:topk]:
        point = faiss_instance_dict[fan_name].p_hu_array[point_id]
        fan_name = FAN_NAMES[point[OffsetPoint.NAME_ID]]
        pack_type = point[OffsetPoint.PACK_TYPE]
        tiles = []
        for tile_id in point[OffsetPoint.TILES: OffsetPoint.TILES + 14]:
            if tile_id == -1:
                break
            tiles.append(TILE_LIST[tile_id])
        if pack_type == PackType.TOTAL:
            wanted_packs = (tuple(tiles),)
        elif pack_type == PackType.BASIC:
            assert len(tiles) % 3 == 0
            wanted_packs = tuple([tuple(tiles[i: i+3]) for i in range(0, len(tiles), 3)])
        elif pack_type == PackType.BASIC_WITH_PAIR:
            assert len(tiles) % 3 == 2
            wanted_packs = (tuple(tiles[0: 2]),) + tuple([tuple(tiles[i: i+3]) for i in range(2, len(tiles), 3)])
        elif pack_type == PackType.QIDUI:
            assert len(tiles) == 14
            wanted_packs = tuple([tiles[i:i + 2] for i in range(0, len(tiles), 2)])

        fan_value = FAN[fan_name]
        res = get_xianten_once(packs, hand, wanted_packs)
        if res:
            res_list.append((fan_name, fan_value, res))
        if len(res_list) >= topk:
            break
    return res_list


def init_faiss_instance(filename):
    if filename.endswith(".npz"):
        npy_array = np.load(filename)['array']
    else:
        npy_array = np.load(filename)
    faiss_instance = faiss.SimpleFAISS(npy_array)
    return faiss_instance


def get_xianten_pengpenghu(packs, hand):
    for pack in packs:
        if len(pack) == 3 and pack[0] != pack[1]:  # 吃
            return None
    rest_tiles_with_info = []
    rest_hand = []

    hand = list(hand)

    for tile in set(hand):
        tile_count = hand.count(tile)
        if tile_count >= 3:
            pass
        elif tile_count == 1 or tile_count == 2:
            rest_tiles_with_info.append((tile, False, True))
        else:
            pass
    return rest_tiles_with_info, rest_hand


def get_xianten_qidui(packs, hand):
    if packs and len(packs) >= 1:  # 有副露
        return None
    
    rest_tiles_with_info = []
    rest_hand = []

    hand = list(hand)

    for tile in set(hand):
        tile_count = hand.count(tile)
        if tile_count == 2 or tile_count == 4:  # 七对或龙七对
            pass
        elif tile_count == 1 or tile_count == 3:  # 七对单张，或龙七对单张
            rest_tiles_with_info.append((tile, False, False))
        else:
            pass
    return rest_tiles_with_info, rest_hand


def get_xianten_quanqiuren(packs, hand):
    # 这里没有暗杠判定，暗杠判定请在外边做

    rest_tiles_with_info = []
    rest_hand = []

    for tile in TILE_LIST:
        tile_type, tile_num = tile[0], int(tile[1])
        round_tiles = []
        for num in [-2, -1, 1, 2]:
            new_tile_num = tile_num + num
            if 1 <= new_tile_num <= 9:
                round_tiles.append(f"{tile_type}{new_tile_num}")
        if hand.count(tile) >= 2 or any(t in hand for t in round_tiles):  # 邻域内有牌，能组成顺子或刻子
            # 想要
            rest_tiles_with_info.append((
                tile,
                any(round_tiles[i] in hand and round_tiles[i + 1] for i in range(len(round_tiles) - 1)),
                hand.count(tile) >= 2
            ))
        elif tile in hand:  # 邻域内只有自己这张牌本身
            rest_hand.append(tile)  # 一般我们不认为全求人会缺对子
    
    return rest_tiles_with_info, rest_hand


def get_xianten_basic(packs, hand, rest_tiles: Dict[str, int]):

    from xianten_utils import BasicFormShanten, UnitType

    rest_tiles_with_info = []
    rest_hand = []

    calculator = BasicFormShanten(packs, hand, rest_tiles)
    calculator.run()
    shanten = calculator.shanten

    if len(hand) % 3 == 1:  # 13张牌，仅考虑哪些牌想要即可。手牌中的孤张将不被认为想要。

        for tile in TILE_LIST:  # 遍历所有牌，只要我们还能抓到它，就抓一下试试；只要抓它能减少向听数，那么它就是我们想要的牌
            if rest_tiles.get(tile, 0) == 0:
                continue
            if tile not in hand:  # 跳过孤张字牌和不靠张的数牌，这些牌都无法减少上听数
                if tile[0] in "FJ":
                    continue
                t = tile[0]
                n = int(tile[1])
                if all(f"{t}{n+p}" not in hand for p in [-2, -1, 1, 2]):
                    continue
            new_hand = hand + (tile,)
            new_calculator = BasicFormShanten(packs, new_hand, rest_tiles)
            new_calculator.run()
            new_shanten = new_calculator.shanten
            if new_shanten < shanten:
                rest_tiles_with_info.append((
                    tile, 
                    any(path_unit.unit_type in [UnitType.CHI_OPEN_END, UnitType.CHI_CLOSED] and path_unit.wanted_tile == tile for work_path in calculator.work_state for path_unit in work_path),
                    any(path_unit.unit_type in [UnitType.INCOMPLETE_PENG] and path_unit.wanted_tile == tile for work_path in calculator.work_state for path_unit in work_path),
                ))
    else:  # 14张牌，仅考虑哪些牌不想要即可。当然你想传入15张牌玩大相公我也不算你错
        for tile in set(hand):  # 遍历所有手牌，尝试把它打出去。只要向听数不变，就说明它是废牌，就是多余的牌，可以打出去
            new_hand = list(hand)
            new_hand.remove(tile)
            new_hand = tuple(new_hand)
            new_calculator = BasicFormShanten(packs, new_hand, rest_tiles)
            new_calculator.run()
            new_shanten = new_calculator.shanten
            if new_shanten == shanten:
                rest_hand.append(tile)
    
    return rest_tiles_with_info, rest_hand

    
def get_xianten_basic_by_lib(packs, hand, rest_tiles):

    from BasicFormShanten import get_xianten_basic

    return get_xianten_basic(packs, hand, rest_tiles)

    from xianten_utils import UnitType

    rest_tiles_with_info = []
    rest_hand = []

    print(hand)
    shanten, useful, workstate = get_xianten_basic(hand, rest_tiles)

    if len(hand) % 3 == 1:  # 13张牌，useful将记录想要的牌
        for tile in useful:
            rest_tiles_with_info.append((
                tile, 
                any(path_unit[0] in [UnitType.CHI_OPEN_END.value, UnitType.CHI_CLOSED.value] and path_unit[2] == tile for work_path in workstate for path_unit in work_path),
                any(path_unit[0] in [UnitType.INCOMPLETE_PENG.value] and path_unit[2] == tile for work_path in workstate for path_unit in work_path),
            ))
    else:  # 14张牌，useful将记录不想要，需要打出的牌
        for tile in useful:
            rest_hand.append(tile)
    
    return rest_tiles_with_info, rest_hand


if __name__ == '__main__':
    s = time.time()
    instance = init_faiss_instance("./data/hupaizuhe.npz")
    e = time.time()
    print(e - s)

    hand_strs = [
        "W1 W1 W1 W2 W3 W4 B5 B6 T7 T8 T9 T9 T9",  # 花龙
        "W1 W2 W4 B2 B7 B9 T1 T4 T6 T9 F1 F1 F2 J3",  # 组合龙
        "W1 W1 B1 B1 T1 T1 W2 W2 B4 B4 T6 T3 T3",  # 七对、小于五
    ]

    for hand_str in hand_strs:
        hand = hand_str.split(" ")

        s = time.time()
        res = get_xianten_all(instance, (), tuple(hand), topk=200)

        print(hand)
        for idx, i in enumerate(res):
            print(f"[{idx}]", len(i[-1][0]), i)

        e = time.time()
        print(e - s)

    hand = "W1 W2 W4 B2 B7 B9 T1 T4 T6 T9 F1 F1 F2 J3".split(" ")
    hu = "W1 W4 W7 B2 B5 B8 T3 T6 T9".split(" ")

    print(instance.distance(np.array([hand_to_point(hu)]), np.array([hand_to_point(hand)])))
    print(instance.distance(np.array([hand_to_point(hand)]), np.array([hand_to_point(hu)])))

    
    TILE_LIST = [
        *("W%d" % (i + 1) for i in range(9)),  # 万
        *("T%d" % (i + 1) for i in range(9)),  # 条
        *("B%d" % (i + 1) for i in range(9)),  # 饼
        *("F%d" % (i + 1) for i in range(4)),  # 风
        *("J%d" % (i + 1) for i in range(3)),  # 箭
    ]

    packs = ()
    hand = tuple(hand)
    rest_tiles = {t: 4 for t in TILE_LIST}
    for t in hand:
        rest_tiles[t] -= 1

    print("python版本计算通用向听：", get_xianten_basic(packs, hand, rest_tiles))

    try:
        print("c++版本计算通用向听：", get_xianten_basic_by_lib(packs, hand, rest_tiles))
    except ImportError:
        print("想使用c++版本，需要执行命令： python setup.py build_ext --inplace")

