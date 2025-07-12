"""
计算凑成各种基本番型所需要的行为，包括想要的牌，以及多余的牌。多余的牌将用于凑齐胡牌剩余的条件，如凑够8番
输入：
pack: Tuple[Tuple[type, tile, int]]
hand: Tuple[tile]

输出：
是否能做: bool
想要的牌: tuple(tile)
多余的牌: tuple(tile)

实现方式：
对于吃牌类的番种，使用打表遍历的方式（如三色三步高、三色三同顺）
对于不限制吃牌，但限制牌类型（如花色、数字、数量）的番种，使用条件判定的方式（如五门齐、混一色、碰碰和）

计算的番种包括（按实战频次排序）：

'三色三步高-6'  118273
'五门齐-6'      57795
'三色三同顺-8'  54314
'花龙-8'        53643
'混一色-6'      44617
'清龙-16'       42694
'碰碰和-6'      33911
'一色三步高-16' 20900
'七对-24'       16372
'全带幺-4'      15410
'清一色-24'     8875
'无番和-8'      8171
'大于五-12'     7620
'组合龙-12'     7272
'小于五-12'     7163
'全不靠-12'     6734
'全求人-6'      5986
'双箭刻-6'      3958
'三暗刻-16'     3916
'七星不靠-24'   3589
'推不倒-8'      2757
'双明杠-4'      1903
'三色三节高-8'  1726
'一色三节高-24' 1610
'小三元-64'     1001
'全带五'        745
'全大-24'       694
'全小-24'       680
'全中-24'       565
'三同刻'        565
'混幺九-32'     542
'一色四步高-32' 485
'三风刻-12'     348
'全双刻-24'     330
'四暗刻-64'     220
'一色三同顺-24' 213
'三色双龙会-16' 144
'三杠-32'       140
'十三幺-88'     101
'大三元-88'     98
'小四喜-64'     62
'一色四节高-48' 45
'字一色-64'     25
'绿一色-88'     17
'清幺九-64'     5
'一色双龙会-64' 5
'连七对-88'     4
'四杠-88'       1
'大四喜-88'     1
"""


import time
import itertools
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
    '荒庄': 0
 }


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
    
    rest_tiles = list(sum(rest_packs, ()))
    rest_hand = list(hand)

    for tile in hand:
        if tile in rest_tiles:
            rest_hand.remove(tile)
            rest_tiles.remove(tile)

    return rest_tiles, rest_hand


def get_xianten_all(packs, hand):
    res_list = []
    for fan_name, fan_value, wanted_pack in WANTED_PACK_VALUES:
        res = get_xianten_once(packs, hand, wanted_pack)
        res_list.append((fan_name, fan_value, res))
    return res_list


WANTED_PACKS = {}
WANTED_PACK_VALUES = []
ijk = ["WBT", "WTB", "BTW", "BWT", "TBW", "TWB"]
wbt = "WBT"


def parse_tilestr(tilestr):
    if isinstance(tilestr, tuple):
        return tilestr
    if isinstance(tilestr, list):
        return tuple(tilestr)
    if isinstance(tilestr, str):
        return tuple(tilestr.split(" "))
    raise TypeError(tilestr)


def regist_wanted_packs(name):
    def inner(function):
        start = time.time()
        WANTED_PACKS[name] = wanted_packs = []
        try:
            iterator = function()
        except NotImplementedError:
            return
        for pack in iterator:
            parsed_pack = tuple(parse_tilestr(i) for i in pack)
            wanted_packs.append(parsed_pack)
            WANTED_PACK_VALUES.append((name, FAN[name], parsed_pack))
        end = time.time()
        print(f"{name} 一共 {len(wanted_packs)} 种情况，遍历耗时 {end - start:.3f}s")
    return inner


@regist_wanted_packs("三色三步高")
def _():
    for i in ijk:
        for n in range(1, 6):
            yield (
                (f"{i[0]}{n}", f"{i[0]}{n + 1}", f"{i[0]}{n + 2}"),
                (f"{i[1]}{n + 1}", f"{i[1]}{n + 2}", f"{i[1]}{n + 3}"),
                (f"{i[2]}{n + 2}", f"{i[2]}{n + 3}", f"{i[2]}{n + 4}"),
            )
    
    
@regist_wanted_packs("三色三同顺")
def _():
    for n in range(1, 8):
        yield (
            (f"W{n} W{n+1} W{n+2}"),
            (f"B{n} B{n+1} B{n+2}"),
            (f"T{n} T{n+1} T{n+2}"),
        )


@regist_wanted_packs("花龙")
def _():
    for i,j,k in ijk:
        yield (
            f"{i}1 {i}2 {i}3",
            f"{j}4 {j}5 {j}6",
            f"{k}7 {k}8 {k}9",
        )


@regist_wanted_packs("清龙")
def _():
    for i in wbt:
        yield (f"{i}1 {i}2 {i}3", f"{i}4 {i}5 {i}6", f"{i}7 {i}8 {i}9")


@regist_wanted_packs("一色三步高")
def _():
    for i in wbt:
        for n in range(1, 6):
            yield f"{i}{n} {i}{n+1} {i}{n+2}",f"{i}{n+1} {i}{n+2} {i}{n+3}",f"{i}{n+2} {i}{n+3} {i}{n+4}",
        for n in range(1, 4):
            yield f"{i}{n} {i}{n+1} {i}{n+2}",f"{i}{n+2} {i}{n+3} {i}{n+4}",f"{i}{n+4} {i}{n+5} {i}{n+6}",


@regist_wanted_packs("组合龙")
def _():
    for i,j,k in ijk:
        yield (f"{i}1 {i}4 {i}7 {j}2 {j}5 {j}8 {k}3 {k}6 {k}9".split(" "), )  # 普通组合龙
        # for p in itertools.combinations(["F1", "F2", "F3", "F4", "J1", "J2", "J3"], 5):  # 全不靠系列的组合龙
        #     yield (f"{i}1 {i}4 {i}7 {j}2 {j}5 {j}8 {k}3 {k}6 {k}9".split(" ") + list(p), )


@regist_wanted_packs("双箭刻")
def _():
    yield "J1 J1 J1", "J2 J2 J2"
    yield "J2 J2 J2", "J3 J3 J3"
    yield "J1 J1 J1", "J3 J3 J3"


@regist_wanted_packs("三色三节高")
def _():
    for i,j,k in ijk:
        for n in range(1, 8):
            yield f"{i}{n} {i}{n} {i}{n}", f"{j}{n+1} {j}{n+1} {j}{n+1}", f"{k}{n+2} {k}{n+2} {k}{n+2}", 


@regist_wanted_packs("一色三节高")
def _():
    for i in wbt:
        for n in range(1, 8):
            yield f"{i}{n} {i}{n} {i}{n}", f"{i}{n+1} {i}{n+1} {i}{n+1}", f"{i}{n+2} {i}{n+2} {i}{n+2}", 


@regist_wanted_packs("小三元")
def _():
    yield "J1 J1 J1", "J2 J2 J2", "J3 J3",
    yield "J1 J1 J1", "J2 J2", "J3 J3 J3",
    yield "J1 J1", "J2 J2 J2", "J3 J3 J3",


@regist_wanted_packs("三同刻")
def _():
    for n in range(1, 10):
        yield f"W{n} W{n} W{n}", f"B{n} B{n} B{n}", f"T{n} T{n} T{n}"


@regist_wanted_packs("一色四步高")
def _():
    for i in wbt:
        for n in range(1, 4):
            yield f"{i}{n} {i}{n+1} {i}{n+2}",f"{i}{n+1} {i}{n+2} {i}{n+3}",f"{i}{n+2} {i}{n+3} {i}{n+4}",f"{i}{n+4} {i}{n+5} {i}{n+6}",
        for n in range(1, 2):
            yield f"{i}{n} {i}{n+1} {i}{n+2}",f"{i}{n+2} {i}{n+3} {i}{n+4}",f"{i}{n+4} {i}{n+5} {i}{n+6}",f"{i}{n+6} {i}{n+7} {i}{n+8}",


@regist_wanted_packs("三风刻")
def _():
    yield "F1 F1 F1", "F2 F2 F2", "F3 F3 F3"
    yield "F1 F1 F1", "F2 F2 F2", "F4 F4 F4"
    yield "F1 F1 F1", "F4 F4 F4", "F3 F3 F3"
    yield "F4 F4 F4", "F2 F2 F2", "F3 F3 F3"
    
    
@regist_wanted_packs("一色三同顺")
def _():
    for i in wbt:
        for n in range(1, 8):
            yield (
                (f"{i}{n} {i}{n+1} {i}{n+2}"),
                (f"{i}{n} {i}{n+1} {i}{n+2}"),
                (f"{i}{n} {i}{n+1} {i}{n+2}"),
            )


@regist_wanted_packs("大三元")
def _():
    yield "J1 J1 J1", "J2 J2 J2", "J3 J3 J3"


@regist_wanted_packs("小四喜")
def _():
    yield "F1 F1 F1", "F2 F2 F2", "F3 F3 F3", "F4 F4"
    yield "F1 F1 F1", "F2 F2 F2", "F3 F3", "F4 F4 F4"
    yield "F1 F1 F1", "F2 F2", "F3 F3 F3", "F4 F4 F4"
    yield "F1 F1", "F2 F2 F2", "F3 F3 F3", "F4 F4 F4"


@regist_wanted_packs("一色四节高")
def _():
    for i in wbt:
        for n in range(1, 7):
            yield f"{i}{n} {i}{n} {i}{n}", f"{i}{n+1} {i}{n+1} {i}{n+1}", f"{i}{n+2} {i}{n+2} {i}{n+2}", f"{i}{n+3} {i}{n+3} {i}{n+3}", 


@regist_wanted_packs("大四喜")
def _():
    yield "F1 F1 F1", "F2 F2 F2", "F3 F3 F3", "F4 F4 F4"


@regist_wanted_packs("一色四同顺")
def _():
    for i in wbt:
        for n in range(1, 8):
            yield f"{i}{n} {i}{n+1} {i}{n+2}", f"{i}{n} {i}{n+1} {i}{n+2}", f"{i}{n} {i}{n+1} {i}{n+2}", f"{i}{n} {i}{n+1} {i}{n+2}", 


TILE_LIST = [
    *("W%d" % (i + 1) for i in range(9)),  # 万
    *("T%d" % (i + 1) for i in range(9)),  # 条
    *("B%d" % (i + 1) for i in range(9)),  # 饼
    *("F%d" % (i + 1) for i in range(4)),  # 风
    *("J%d" % (i + 1) for i in range(3)),  # 箭
]

YAOJIU_TILE_LIST = "W1 W9 B1 B9 T1 T9 F1 F2 F3 F4 J1 J2 J3".split(" ")
TUIBUDAO_TILE_LIST = "B1 B2 B3 B4 B5 B8 B9 T2 T4 T5 T6 T8 J3".split(" ")
    
    
@regist_wanted_packs("三色双龙会")
def _():
    for i,j,k in ijk:
        yield f"{i}1 {i}2 {i}3", f"{i}1 {i}2 {i}3", f"{j}5 {j}5", f"{k}7 {k}8 {k}9", f"{k}7 {k}8 {k}9"
    
    
@regist_wanted_packs("一色双龙会")
def _():
    for i in wbt:
        yield f"{i}1 {i}2 {i}3", f"{i}1 {i}2 {i}3", f"{i}5 {i}5", f"{i}7 {i}8 {i}9", f"{i}7 {i}8 {i}9"
    
    
@regist_wanted_packs("连七对")
def _():
    for i in wbt:
        yield f"{i}1 {i}1", f"{i}2 {i}2", f"{i}3 {i}3", f"{i}4 {i}4", f"{i}5 {i}5", f"{i}6 {i}6", f"{i}7 {i}7", 
        yield f"{i}2 {i}2", f"{i}3 {i}3", f"{i}4 {i}4", f"{i}5 {i}5", f"{i}6 {i}6", f"{i}7 {i}7", f"{i}8 {i}8", 
        yield f"{i}3 {i}3", f"{i}4 {i}4", f"{i}5 {i}5", f"{i}6 {i}6", f"{i}7 {i}7", f"{i}8 {i}8", f"{i}9 {i}9", 


@regist_wanted_packs("组合不靠")
def _():
    for i,j,k in ijk:
        for p in itertools.combinations(["F1", "F2", "F3", "F4", "J1", "J2", "J3"], 5):  # 全不靠系列的组合龙
            yield (f"{i}1 {i}4 {i}7 {j}2 {j}5 {j}8 {k}3 {k}6 {k}9".split(" ") + list(p), )


@regist_wanted_packs("五门齐")
def _():
    """
    所有基本胡型情况全部遍历。
    注意，五门七对的情况有19840464种情况，无法全部枚举。如果要每种胡型都单独考虑七对型，那么五门七对需要使用贪心策略单独列举
    目前的策略为所有胡型的七对全都不枚举，七对型与基本胡型作为并列的情况分别考虑
    """
    packs = [[i, i, i] for i in range(1, 10)] + [[i, i+1, i+2] for i in range(1, 8)]  # WBT的顺子、刻子全排列
    pairs = [[i, i] for i in range(1, 10)]  # WBT的对子全排列
    f_packs = [[i, i, i] for i in ["F1", "F2", "F3", "F4"]]
    f_pairs = [[i, i] for i in ["F1", "F2", "F3", "F4"]]
    j_packs = [[i, i, i] for i in ["J1", "J2", "J3"]]
    j_pairs = [[i, i] for i in ["J1", "J2", "J3"]]

    combines = [
        [pairs, packs, packs, f_packs, j_packs],
        [packs, pairs, packs, f_packs, j_packs],
        [packs, packs, pairs, f_packs, j_packs],
        [packs, packs, packs, f_pairs, j_packs],
        [packs, packs, packs, f_packs, j_pairs],
    ]
    
    for combine in combines:
        for w in combine[0]:
            for b in combine[1]:
                for t in combine[2]:
                    for f in combine[3]:
                        for j in combine[4]:
                            yield tuple(f"W{i}" for i in w), tuple(f"B{i}" for i in b), tuple(f"T{i}" for i in t), tuple(f"{i}" for i in f), tuple(f"{i}" for i in j)


@regist_wanted_packs("混一色")
def _():
    """
    计算方法：选择一种颜色，将剩余两种颜色的牌视为废牌，然后使用通用方法计算向听
    """
    packs = [[i, i, i] for i in range(1, 10)] + [[i, i+1, i+2] for i in range(1, 8)]  # WBT的顺子、刻子全排列
    pairs = [[i, i] for i in range(1, 10)]  # WBT的对子全排列
    f_packs = [[i, i, i] for i in ["F1", "F2", "F3", "F4"]]
    f_pairs = [[i, i] for i in ["F1", "F2", "F3", "F4"]]
    j_packs = [[i, i, i] for i in ["J1", "J2", "J3"]]
    j_pairs = [[i, i] for i in ["J1", "J2", "J3"]]

    for i in wbt:
        curr_valid_packs = [tuple(f"{i}{j}" for j in pack) for pack in packs] + f_packs + j_packs
        curr_valid_pairs = [tuple(f"{i}{j}" for j in pack) for pack in pairs] + f_pairs + j_pairs
        for pair in curr_valid_pairs:
            for p1, p2, p3, p4 in itertools.combinations(curr_valid_packs, 4):
                yield p1, p2, p3, p4, pair
        for ps in itertools.combinations(curr_valid_pairs, 7):  # 七对型
            yield ps


@regist_wanted_packs("碰碰和")
def _():
    """
    计算方法：首先确认packs里面没有吃，然后使用贪心方法遍历手牌的对子
    """
    raise NotImplementedError
    # for p1, p2, p3, p4, p5 in itertools.combinations(TILE_LIST, 5):
    #     yield (p1, p1, p1), (p2, p2, p2), (p3, p3, p3), (p4, p4, p4), (p5, p5)
    #     yield (p1, p1, p1), (p2, p2, p2), (p3, p3, p3), (p4, p4), (p5, p5, p5)
    #     yield (p1, p1, p1), (p2, p2, p2), (p3, p3), (p4, p4, p4), (p5, p5, p5)
    #     yield (p1, p1, p1), (p2, p2), (p3, p3, p3), (p4, p4, p4), (p5, p5, p5)
    #     yield (p1, p1), (p2, p2, p2), (p3, p3, p3), (p4, p4, p4), (p5, p5, p5)


@regist_wanted_packs("七对")
def _():
    """
    计算方法：确认packs为空，然后去除手牌中所有对子，最后返回所有单牌
    """
    raise NotImplementedError  # 34选7，共18828656种情况，无法硬遍历


@regist_wanted_packs("全带幺")
def _():
    """
    计算方法：可行的pack只有：111、123、999、987、11、99，WBT共18种，加上字牌的刻子、对子共14种，总计32种。
    此外还有幺九七对的情况（属于混幺九），枚举遍历即可，共C(13, 7)=1716种情况
    """
    packs = [(i, i, i) for i in YAOJIU_TILE_LIST] + [("W1", "W2", "W3"), ("W7", "W8", "W9"), ("B1", "B2", "B3"), ("B7", "B8", "B9"), ("T1", "T2", "T3"), ("T7", "T8", "T9"), ] * 4
    pairs = [(i, i) for i in YAOJIU_TILE_LIST]
    for pair in pairs:
        for p1, p2, p3, p4 in itertools.combinations(packs, 4):
            yield p1, p2, p3, p4, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("清一色")
def _():
    """
    计算方法：选择一种颜色，将剩余两种颜色的牌和字牌视为废牌，然后使用通用方法计算向听
    """
    packs = [[i, i, i] for i in range(1, 10)] + [[i, i+1, i+2] for i in range(1, 8)]  # WBT的顺子、刻子全排列
    pairs = [[i, i] for i in range(1, 10)]  # WBT的对子全排列

    for i in wbt:
        curr_valid_packs = [tuple(f"{i}{j}" for j in pack) for pack in packs]
        curr_valid_pairs = [tuple(f"{i}{j}" for j in pack) for pack in pairs]
        for pair in curr_valid_pairs:
            for p1, p2, p3, p4 in itertools.combinations(curr_valid_packs, 4):
                yield p1, p2, p3, p4, pair
        # for ps in itertools.combinations(curr_valid_pairs, 7):  # 七对型
        #     yield ps


@regist_wanted_packs("无番和")
def _():
    """
    计算方法：要求packs不满、无幺九刻、123123、123789、123456、双同刻、不缺门。
    """
    pairs = [(i, i) for i in "F1 F2 F3 F4 J1 J2 J3".split(" ")]
    packs = set([tuple([f"{i}{j}", f"{i}{j}", f"{i}{j}"]) for i in "WBT" for j in range(2, 9)])
    chi_packs = set([tuple([f"{i}{j - 1}", f"{i}{j}", f"{i}{j + 1}"]) for i in "WBT" for j in range(2, 9)])
    for pair in pairs:
        for plist in itertools.combinations(packs | chi_packs, 4):  # 无番和不能一般高，所以不会有一样的顺子出现
            if not all(p in packs for p in plist) and not all(p in chi_packs for p in plist):
                yield *plist, pair


@regist_wanted_packs("大于五")
def _():
    """
    计算方法：可行的pack只有：666、777、888、999、678、789、66、77、88、99，WBT共30种pack，以及大于五的七对，共C(12, 7)=792种情况
    """
    pairs = [(i, i) for i in "W6 W7 W8 W9 B6 B7 B8 B9 T6 T7 T8 T9".split(" ")]
    packs = [(i, i, i) for i in "W6 W7 W8 W9 B6 B7 B8 B9 T6 T7 T8 T9".split(" ")]
    chi_packs = [("W6", "W7", "W8"), ("W7", "W8", "W9"), ("B6", "B7", "B8"), ("B7", "B8", "B9"), ("T6", "T7", "T8"), ("T7", "T8", "T9")]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("小于五")
def _():
    """
    计算方法：可行的pack只有：111、222、333、444、123、234、11、22、33、44，WBT共30种pack，以及小于五的七对，共C(12, 7)=792种情况
    """
    pairs = [(i, i) for i in "W1 W2 W3 W4 B1 B2 B3 B4 T1 T2 T3 T4".split(" ")]
    packs = [(i, i, i) for i in "W1 W2 W3 W4 B1 B2 B3 B4 T1 T2 T3 T4".split(" ")]
    chi_packs = [("W1", "W2", "W3"), ("W2", "W3", "W4"), ("B1", "B2", "B3"), ("B2", "B3", "B4"), ("T1", "T2", "T3"), ("T2", "T3", "T4")]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("全不靠")
def _():
    """
    计算方法：将可能的全不靠可能性全部遍历并返回，返回一个长度为14的大pack。共6*C(16, 14)=720种情况
    """
    for i,j,k in ijk:
        tilelist = f"{i}1 {i}4 {i}7 {j}2 {j}5 {j}8 {k}3 {k}6 {k}9 F1 F2 F3 F4 J1 J2 J3".split(" ")
        for i in itertools.combinations(tilelist, 14):
            yield (i, )


@regist_wanted_packs("全求人")
def _():
    """
    计算方法：使用通用方法计算。
    """
    raise NotImplementedError


@regist_wanted_packs("三暗刻")
def _():
    """
    计算方法：packs数量不超过1，然后使用贪心算法尝试在手牌中凑出3个暗刻。
    """
    raise NotImplementedError


@regist_wanted_packs("七星不靠")
def _():
    """
    计算方法：将可能的七星不靠可能性全部遍历并返回，返回一个长度为14的大pack。共6*C(9, 7) = 216种情况
    """
    for i,j,k in ijk:
        tilelist = f"{i}1 {i}4 {i}7 {j}2 {j}5 {j}8 {k}3 {k}6 {k}9".split(" ")
        for pack in itertools.combinations(tilelist, 7):
            yield (pack + tuple("F1 F2 F3 F4 J1 J2 J3".split(" ")), )


@regist_wanted_packs("推不倒")
def _():
    """
    计算方法：将B1234589、T245689、J3以外的牌视为废牌。七对的情况有C(14, 7)=3432种
    """
    pairs = [(i, i) for i in TUIBUDAO_TILE_LIST]
    packs = [(i, i, i) for i in TUIBUDAO_TILE_LIST]
    chi_packs = [("B1", "B2", "B3"), ("B2", "B3", "B4"), ("B3", "B4", "B5"), ("T4", "T5", "T6")]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("全带五")
def _():
    """
    计算方法：可行的pack只有：345、456、567、555、55，WBT加起来共15种pack，结合手牌情况做贪心排列组合。不可能有七对的情况。
    """
    pairs = [(i, i) for i in "W5 B5 T5".split(" ")]
    packs = [(i, i, i) for i in "W5 B5 T5".split(" ")]
    chi_packs = [("W3", "W4", "W5"), ("W4", "W5", "W6"), ("W5", "W6", "W7"),
                 ("B3", "B4", "B5"), ("B4", "B5", "B6"), ("B5", "B6", "B7"),
                 ("T3", "T4", "T5"), ("T4", "T5", "T6"), ("T5", "T6", "T7"),]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair


@regist_wanted_packs("全大")
def _():
    """
    计算方法：可行的pack只有：777、888、999、789、77、88、99，WBT加起来共21种情况，结合手牌情况做贪心排列组合；全大七对共C(9, 7)=36种情况
    """
    pairs = [(i, i) for i in "W7 W8 W9 B7 B8 B9 T7 T8 T9".split(" ")]
    packs = [(i, i, i) for i in "W7 W8 W9 B7 B8 B9 T7 T8 T9".split(" ")]
    chi_packs = [("W7", "W8", "W9"), ("B7", "B8", "B9"), ("T7", "T8", "T9")]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("全小")
def _():
    """
    计算方法：可行的pack只有：111、222、333、123、11、22、33，WBT加起来共21种情况，结合手牌情况做贪心排列组合；全小七对共C(9, 7)=36种情况
    """
    pairs = [(i, i) for i in "W1 W2 W3 B1 B2 B3 T1 T2 T3".split(" ")]
    packs = [(i, i, i) for i in "W1 W2 W3 B1 B2 B3 T1 T2 T3".split(" ")]
    chi_packs = [("W1", "W2", "W3"), ("B1", "B2", "B3"), ("T1", "T2", "T3")]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("全中")
def _():
    """
    计算方法：可行的pack只有：444、555、666、456、44、55、66，WBT加起来共21种情况，结合手牌情况做贪心排列组合；全中七对共C(9, 7)=36种情况
    """
    pairs = [(i, i) for i in "W4 W5 W6 B4 B5 B6 T4 T5 T6".split(" ")]
    packs = [(i, i, i) for i in "W4 W5 W6 B4 B5 B6 T4 T5 T6".split(" ")]
    chi_packs = [("W4", "W5", "W6"), ("B4", "B5", "B6"), ("T4", "T5", "T6")]
    for pair in pairs:
        for plist in itertools.combinations(packs + chi_packs * 4, 4):
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("混幺九")
def _():
    """
    计算方法：可行的pack只有：幺九刻、对子共26种pack；幺九七对，视为一个长度为14的大pack，一共C(13, 7)=1716种情况
    """
    pairs = [(i, i) for i in YAOJIU_TILE_LIST]
    packs = [(i, i, i) for i in YAOJIU_TILE_LIST]
    for pair in pairs:
        for plist in itertools.combinations(packs, 4):  # 基本型
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("全双刻")
def _():
    """
    计算方法：可行的pack只有：2468WBT共12种刻子和对子，共24种情况；全双七对，共C(12, 7)=792种情况
    """
    pairs = [(i, i) for i in "W2 W4 W6 W8 B2 B4 B6 B8 T2 T4 T6 T8".split(" ")]
    packs = [(i, i, i) for i in "W2 W4 W6 W8 B2 B4 B6 B8 T2 T4 T6 T8".split(" ")]
    for pair in pairs:
        for plist in itertools.combinations(packs, 4):  # 基本型
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("四暗刻")
def _():
    """
    计算方法：要求packs长度为0，然后使用贪心算法在手牌中凑出4个暗刻
    """
    raise NotImplementedError


@regist_wanted_packs("十三幺")
def _():
    """
    计算方法：将胡牌的情况作为一个14张的大pack，共13种情况，全部遍历并返回
    """
    for tile in YAOJIU_TILE_LIST:
        yield (((tile,) + tuple(YAOJIU_TILE_LIST)), )


@regist_wanted_packs("字一色")
def _():
    """
    计算方法：可行的pack一共只有7种字牌的刻子、对子，以及字七对（仅一种情况）
    """
    pairs = [(i, i) for i in "F1 F2 F3 F4 J1 J2 J3".split(" ")]
    packs = [(i, i, i) for i in "F1 F2 F3 F4 J1 J2 J3".split(" ")]
    for pair in pairs:
        for plist in itertools.combinations(packs, 4):  # 基本型
            yield *plist, pair
    # for ps in itertools.combinations(pairs, 7):  # 七对型
    #     yield ps


@regist_wanted_packs("绿一色")
def _():
    """
    计算方法：可行的pack一共只有T23468、J2的刻子、对子，以及T234这一种顺子。不可能有七对。
    """
    pairs = [(i, i) for i in "T2 T3 T4 T6 T8 J2".split(" ")]
    packs = [(i, i, i) for i in "T2 T3 T4 T6 T8 J2".split(" ")]
    for pair in pairs:
        for plist in itertools.combinations(packs, 4):
            yield *plist, pair


@regist_wanted_packs("清幺九")
def _():
    """
    计算方法：可行的pack一共只有WBT19的刻子、对子。不可能有七对。
    """
    pairs = [(i, i) for i in "W1 W9 B1 B9 T1 T9".split(" ")]
    packs = [(i, i, i) for i in "W1 W9 B1 B9 T1 T9".split(" ")]
    for pair in pairs:
        for plist in itertools.combinations(packs, 4):
            yield *plist, pair



"""
结合以上函数，我们可以做到一件事情：
给定一组牌，最大向听数和一个给定的方向，以及当前牌河内剩余的牌
能够划定一个手牌范围，范围内的牌用于构成胡牌所需的牌，范围外的牌用于打出或构成其它小番，此外还能明确自己需要的牌的获取方式（能不能吃、能不能碰）

一共有22+24=46种主要大番种（除全不靠、不求人、杠子系列），假设每种方向取top10，则一共460组可以做的牌
每组牌的特征包括：
最小番数（即当前做牌方向的番，不考虑其它可能的番）
34张牌的进张方式（抓、吃、碰杠，3个维度）
34张牌的多余牌数量（0~4，1个维度）
34张牌的剩余张数（0~4，1个维度）
每组牌171维，460组牌加起来就是78600维
实际上，这460组牌是特别特别稀疏的，可以全体放在一起取top10，10组牌就是1710维，top50就是50组牌，8550维，这样就没那么可怕了
当然，具体能不能取top50还得遍历所有测试集中的手牌情况，根据统计结果做决定
此外需要考虑模型结构。
我们让20层res_block拟合剩余需要凑齐的1~4番，共4608维，模型大小约30M
所以后续全连接层如果仍然保持为3层，则模型大小不能超过200M
top30的话，全连接层大小为103M，全模型加起来约150~160M，差不多了

实际上，由于以上vec的特征实在是太明显了，我们完全可以只使用2层全连接，第一层降维，第二层输出，虽然两层模型只能拟合简单情况，但特征本就很明显了，不需要太复杂的操作
但这样做的话，就必须论证我给出的大量特征只需要简单的线性组合就可以得出足够准确的结论。

当做牌方向十分显然时，每个可用于解释行为的特征都是显然的。
然而，我们还需要考虑剩余那些牌的做牌方向。虽然剩余的牌数量不多，最多也就是5张（双箭刻的话是8张），但上述特征并未涵盖它们，所以两层神经网络未必就好使

假设每个番种之间相互独立，互不干扰
那么，每个番种使用1层全连接层得到235维向量，模型大小维0.15M，46个番种就是7M
由于进张方式直接映射到是否吃碰杠，多余牌数量直接映射到打什么牌，所以1层全连接是理论可行的

即使想保险一点，使用3层全连接做足够的思考，171->128->128->235，每个模型也就是0.26M，46个模型加起来是12M，完全可行

于是模型结构如下：

resnet+vec 4608+117=4725维 --> 48维分类器

其中，前46维为上述番种
第47维为全不靠
第48维为小番大杂烩（一堆1、2、4番的番种加起来组合成8番）

然后取超过阈值的那些类别，每个类别计算一个行为概率，最后将这些行为概率按照分类器的概率加权求和，得到最终结果
注意，不需要直接计算行为概率，可以计算行为概率的扰动。
比方说，我打W1和W4都可以做成三色三步高，那么我初始的概率就是[0.5, 0.5]，模型只需要去计算我应该打哪个，不需要去计算我哪些不需要考虑。
这是因为，对模型来说，学习扰动比学习决策要容易得多

"""


"""
现在考虑如何做上面24个番种的做牌方向。
以上这些可以分为几类：
1. 部分牌视为非法，其余牌使用通用算法确定做牌方向
2. pack排列组合有限
3. 启发式算法，一定范围内计算做牌方向

1类包括：混一色，全带幺，清一色，推不倒
2类包括：大于五，小于五，全不靠，七星不靠，全带五，全大，全小，全中，混幺九，全双刻，十三幺，字一色，绿一色，清幺九
3类包括：五门齐，碰碰和，七对，无番和，三暗刻，四暗刻

由此可以确定，我需要以下通用函数，分别解决这些类问题：

通用基本向听函数，部分牌视为非法时，使用DFS遍历计算基本型向听方向
get_xianten_basic(packs, hand, invalid_tiles, max_shanten, rest_tiles)

通用七对向听函数，部分牌视为非法时，使用DFS遍历计算七对型向听方向（七对也可使用此方法）
get_xianten_qidui(packs, hand, invalid_tiles, max_shanten, rest_tiles)

指定基本向听函数，部分pack已经指定范围的情况下，使用DFS遍历计算基本型向听方向（全不靠、十三幺、组合龙视为一个长度为14或9，只能抓的大pack）
（碰碰和、三暗刻、四暗刻也可使用此方法）
（注意，只计算基本胡型，七对胡型使用通用七对向听函数，并将范围外的牌视为非法即可）
get_xianten_with_packs(packs, hand, wanted_packs, max_shanten, rest_tiles)

锚点基本向听函数，对于一副牌和指定的锚点，使用DFS遍历计算基本型向听方向，用于计算五门齐，同时作为无番和的参考实现
get_xianten_archor(packs, hand, archor_tiles, max_shanten, rest_tiles)

还剩下五门齐、无番和两种情况，需单独处理

五门齐可以使用普通启发式算法，首先每一类牌选择一个锚点，然后以锚点为中心尝试遍历刻子、对子与顺子，使用贪心遍历。

无番和可以使用普通启发式算法，要有一个字牌对子，一个暗刻，不能有杠，万饼条都要有牌，然后使用通用锚点算法确定做牌方向。注意，遍历时，需要回避以下番种：
单吊、坎张、边张、幺九刻、老少副、连六、喜相逢、一般高、双暗刻、双同刻、四归一、胡绝张、全带幺。

无法回避的番种：自摸、门前清、不求人
已经回避的番种：无字、缺门、明杠、断幺、暗杠、平和、幺九刻的升级版（门风刻、圈风刻、箭刻）
"""

with open("packs.pickle", "wb") as fs:
    import pickle
    pickle.dump(WANTED_PACKS, fs)

print("start load")
s = time.time()
with open("packs.pickle", "rb") as fs:
    import pickle
    pickle.load(fs)
e = time.time()
print("end load")
print(e - s)
