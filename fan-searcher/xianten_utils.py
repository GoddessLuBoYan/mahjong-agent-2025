"""
修改函数定位：仅用于计算通用基本向听，不考虑番种数量和大小
"""


from enum import Enum
from typing import Tuple, Dict, List
from std_utils import *


UnitType = str  # 吃CHI, 碰PENG, 对子DUI, 两面或者边张搭子CHI_OPEN_END, 坎张搭子CHI_CLOSED, 刻子搭子PENG_INCOMPLETE
Tile = str
PathUnit = Tuple[Tile]
WorkPath = List[PathUnit]
WorkState = List[WorkPath]


TileTable = Dict[str, int]
UsefulTable = Dict[str, int]


def get_xianten_basic(packs: Tuple[Tuple[str]], hand: Tuple[str], invalid_tiles: Tuple[str], max_shanten: int, rest_tiles: TileTable):
    """
    通用基本向听函数，只做3*4+2=14这种基本型，部分牌视为非法时，使用DFS遍历计算基本型向听方向

    思路：
    参考MahjongGB，穷举所有的合法牌，获取能减少上听数的牌
    首先计算上听数
    然后穷举所有的牌，获取能减少上听数的牌
    """
    raise NotImplementedError


class UnitType(Enum):
    CHI = 1
    PENG = 2
    PAIR = 4
    CHI_OPEN_END = 5
    CHI_CLOSED = 6
    INCOMPLETE_PENG = 7


# 不确定python3.6环境是否安装了dataclass，保险起见采用手动实现以下功能
# dataclass(frozen=True, order=True, unsafe_hash=True)
class PathUnit:
    def __init__(self, unit_type: UnitType, unit: Tuple[str], wanted_tile: str = ""):
        self.__unit_type = unit_type
        self.__unit = tuple(unit)
        self.__wanted_tile = wanted_tile
    
    def __str__(self):
        if self.wanted_tile:
            return repr((*self.unit, f"[[{self.wanted_tile}]]"))
        return repr(self.unit)
    
    __repr__ = __str__

    ### frozen = True
    @property
    def unit_type(self):
        return self.__unit_type
    
    @property
    def unit(self):
        return self.__unit
    
    @property
    def wanted_tile(self):
        return self.__wanted_tile
    
    ### unsafe_hash = True
    def __hash__(self):
        return str.__hash__(repr(self))
    
    ### order = True

    def __lt__(self, other):
        return str(self).__lt__(str(other))

    def __le__(self, other):
        return str(self).__le__(str(other))

    def __eq__(self, other):
        return str(self).__eq__(str(other))

    def __ne__(self, other):
        return str(self).__ne__(str(other))

    def __gt__(self, other):
        return str(self).__gt__(str(other))

    def __ge__(self, other):
        return str(self).__ge__(str(other))
    

class BasicFormShanten:
    """
    用于递归计算上听数的工具类
    """

    TILE_LIST = [
            *("W%d" % (i + 1) for i in range(9)),  # 万
            *("T%d" % (i + 1) for i in range(9)),  # 条
            *("B%d" % (i + 1) for i in range(9)),  # 饼
            *("F%d" % (i + 1) for i in range(4)),  # 风
            *("J%d" % (i + 1) for i in range(3)),  # 箭
        ]

    def __init__(self, packs: Tuple[Tuple[str]], hand: Tuple[str], rest_tiles: TileTable):
        self.packs = packs
        self.hand = hand
        self.invalid_tiles = []
        self.rest_tiles = rest_tiles

        self.shanten = 20  # 向听数，0表示听牌，-1表示已经和了

        self.valid_tiles = [t for t in self.TILE_LIST if t not in self.invalid_tiles]

        self.cnt_table = {tile: self.hand.count(tile) for tile in self.valid_tiles}  # 合法的手牌情况
        self.invalid_tile_count = sum(self.hand.count(tile) for tile in self.invalid_tiles)  # 不合法的手牌数量
        self.valid_rest_tiles = {tile: (count if tile in self.valid_tiles else 0) for tile, count in self.rest_tiles.items()}
        self.has_pair = False
        self.pack_cnt = len(self.packs)
        self.incomplete_cnt = 0
        self.work_path: List[PathUnit] = []
        self.work_state: List[List[PathUnit]] = []

    def run(self):
        self.shanten = self.walk()

    def exists_work_path(self):
        return any(std_includes(path, sorted(self.work_path)) for path in self.work_state)

    def save_work_path(self):
        self.work_state.append(sorted(self.work_path))

    def walk(self):
        # 如果已经有4个副露，那么如果某一张牌有至少两张手牌，就是和了，没有就是听牌
        if len(self.packs) == 4:
            for t in self.valid_tiles:
                if self.cnt_table[t] > 1:
                    return -1
            return 0

        # 如果已经组成了4个面子，那么如果有雀头，就是和了，没有就是听牌
        if self.pack_cnt == 4:
            if self.has_pair:
                return -1
            return 0
        
        # 算法说明：
        # 缺少的面子数=4-完成的面子数
        # 缺少的搭子数=缺少的面子数-已有的搭子数
        # 两式合并：缺少的搭子数=4-完成的面子数-已有的搭子数
        incomplete_need = 4 - self.pack_cnt - self.incomplete_cnt
        if incomplete_need > 0:  # 还需要搭子的情况
            # 每个搭子需要1张，每个单张需要2张；如果还没有雀头，那么其中一个单张将用于组雀头，只需要一张
            
            max_ret = self.incomplete_cnt + incomplete_need * 2 - (1 if self.has_pair else 0)
        else:  # 搭子齐了的情况
            # 有雀头时，上听数 = 3 - 完成的面子数
            # 无雀头时，上听数 = 4 - 完成的面子数
            max_ret = (3 if self.has_pair else 4) - self.pack_cnt
        
        result = max_ret
        
        if self.pack_cnt + self.incomplete_cnt > 4:  # 搭子超载
            # 搭子已经足够多了，每个搭子只需要1张即可组成面子，所以搭子数就是向听数
            self.save_work_path()
            return max_ret
        
        # 搭子还不足够多，需要遍历所有手牌，尝试组搭子
        # 如果组成了搭子，那么向听数将会因此而减少，否则就不会减少
        for t in self.valid_tiles:  # 只考虑合法的牌，不合法的牌不考虑
            if self.cnt_table[t] < 1:  # 手里没有这张牌
                continue

            t_type = t[0]
            t_num = int(t[1])

            # 雀头
            if not self.has_pair and self.cnt_table[t] > 1:
                unit = PathUnit(UnitType.PAIR, (t, t))  # 记录雀头
                self.work_path.append(unit)
                if not self.exists_work_path():  # 还没有记录过这条路径
                    # 削减雀头，递归
                    self.cnt_table[t] -= 2
                    tmp = self.has_pair
                    self.has_pair = True
                    
                    ret = self.walk()
                    result = min(ret, result)
                    # 还原
                    self.cnt_table[t] += 2
                    self.has_pair = tmp
                # 还原
                self.work_path.remove(unit)

            # 刻子
            if self.cnt_table[t] > 2: 
                unit = PathUnit(UnitType.PENG, (t, t, t))  # 记录刻子
                self.work_path.append(unit)
                if not self.exists_work_path():  # 还没有记录过这条路径
                    # 削减刻子，递归
                    self.cnt_table[t] -= 3
                    self.pack_cnt += 1

                    ret = self.walk()
                    result = min(ret, result)
                    # 还原
                    self.cnt_table[t] += 3
                    self.pack_cnt -= 1
                # 还原
                self.work_path.remove(unit)
            
            # 顺子（只能是数字牌，且顺子三张牌均需合法）
            if t_type in "WBT" and t_num <= 7:
                t1 = f"{t_type}{t_num + 1}"
                t2 = f"{t_type}{t_num + 2}"
                if t1 in self.valid_tiles and t2 in self.valid_tiles \
                        and self.cnt_table[t1] > 0 and self.cnt_table[t2] > 0:
                    unit = PathUnit(UnitType.CHI, (t, t1, t2))  # 记录顺子
                    self.work_path.append(unit)
                    if not self.exists_work_path():  # 还没有记录过这条路径
                        # 削减顺子，递归
                        self.cnt_table[t] -= 1
                        self.cnt_table[t1] -= 1
                        self.cnt_table[t2] -= 1
                        self.pack_cnt += 1

                        ret = self.walk()
                        result = min(ret, result)

                        # 还原
                        self.cnt_table[t] += 1
                        self.cnt_table[t1] += 1
                        self.cnt_table[t2] += 1
                        self.pack_cnt -= 1
                    # 还原
                    self.work_path.remove(unit)

            # 如果已经通过削减雀头/面子降低了上听数，再按搭子计算的上听数肯定不会更少
            if result < max_ret:
                continue

            # 刻子搭子
            if self.cnt_table[t] > 1 and self.valid_rest_tiles[t] > 1:
                unit = PathUnit(UnitType.INCOMPLETE_PENG, (t, t), t)
                self.work_path.append(unit)
                if not self.exists_work_path():
                    # 削减刻子搭子，递归
                    self.cnt_table[t] -= 2
                    self.valid_rest_tiles[t] -= 1
                    self.incomplete_cnt += 1
                    
                    ret = self.walk()
                    result = min(ret, result)
                    # 还原
                    self.cnt_table[t] += 2
                    self.valid_rest_tiles[t] += 1
                    self.incomplete_cnt -= 1
                self.work_path.remove(unit)

            # 顺子搭子（只能是数牌，且组成的顺子均需合法）
            if t_type in "WBT":
                # 两面或者边张搭子t t+1，显然t不能是9点以上的数牌，且搭子组成的顺子中至少有一个是合法的
                if t_num < 9:
                    t1 = f"{t_type}{t_num + 1}"
                    t2_list = []
                    if t_num != 8:  # 只要不是8 9 10就行
                        t2_list.append(f"{t_type}{t_num + 2}")
                    if t_num != 1:  # 只要不是1 2 0就行
                        t2_list.append(f"{t_type}{t_num - 1}")
                    for t2 in t2_list:
                        if self.cnt_table[t1] > 0 and self.valid_rest_tiles[t2] > 0:
                            # 记录两面或者边张搭子，其中想要的第三张牌是合法的
                            unit = PathUnit(UnitType.CHI_OPEN_END, (t, t1), t2)
                            self.work_path.append(unit)
                            if not self.exists_work_path():
                                # 削减顺子搭子，递归
                                self.cnt_table[t] -= 1
                                self.cnt_table[t1] -= 1
                                self.valid_rest_tiles[t2] -= 1
                                self.incomplete_cnt += 1
                                
                                ret = self.walk()
                                result = min(ret, result)
                                # 还原
                                self.cnt_table[t] += 1
                                self.cnt_table[t1] += 1
                                self.valid_rest_tiles[t2] += 1
                                self.incomplete_cnt -= 1
                            self.work_path.remove(unit)

                if t_num < 8:
                    # 坎张搭子
                    t1 = f"{t_type}{t_num + 2}"
                    t2 = f"{t_type}{t_num + 1}"
                    if self.cnt_table[t1] > 0 and self.valid_rest_tiles[t2] > 0:
                        # 记录坎张搭子，其中想要的第三张牌是合法的
                        unit = PathUnit(UnitType.CHI_OPEN_END, (t, t1), t2)
                        self.work_path.append(unit)
                        if not self.exists_work_path():
                            # 削减顺子搭子，递归
                            self.cnt_table[t] -= 1
                            self.cnt_table[t1] -= 1
                            self.valid_rest_tiles[t2] -= 1
                            self.incomplete_cnt += 1
                            
                            ret = self.walk()
                            result = min(ret, result)
                            # 还原
                            self.cnt_table[t] += 1
                            self.cnt_table[t1] += 1
                            self.valid_rest_tiles[t2] += 1
                            self.incomplete_cnt -= 1
                        self.work_path.remove(unit)

        # 如果遍历了所有手牌，向听数都没有因此减少
        # 那么现在这种情况就算是当前的最优情况了，记录下来
        if result == max_ret:
            self.save_work_path()

        return result


if __name__ == '__main__':
    packs = ()
    hand = tuple("W1 W2 W5 W6 B2 B3 B4 B8 B8 T8 T8 T9 J1".split(" "))
    invalid_tiles = tuple([f"{i}{j}" for i in "BT" for j in range(1, 10)])
    rest_tiles = {i: 4 for i in BasicFormShanten.TILE_LIST}
    for h in hand:
        rest_tiles[h] -= 1

    print("当前手牌: ")
    print(*hand)

    print("不考虑当前牌局情况，向听计算结果：")
    calcator = BasicFormShanten(packs, hand, rest_tiles)
    calcator.run()
    print(calcator.shanten)

    for work_path in calcator.work_state:
        print(work_path)

    print("考虑当前牌局情况（假设B、T都打光了），向听计算结果：")
    for t in invalid_tiles:
        rest_tiles[t] = 0

    calcator = BasicFormShanten(packs, hand, rest_tiles)
    calcator.run()
    print(calcator.shanten)

    for work_path in calcator.work_state:
        print(work_path)

    print("遍历所有可以抓的牌，计算如果抓到了这张牌，新的向听数将会是多少。（如果新的向听数不增加，则这张牌是想要的牌）")
    for t in BasicFormShanten.TILE_LIST:
        if t not in rest_tiles or rest_tiles[t] < 1:
            continue
        new_hand = list(hand)
        new_hand.append(t)
        new_hand = tuple(new_hand)
        new_calcator = BasicFormShanten(packs, new_hand, rest_tiles)
        new_calcator.run()
        print("抓", t, "，向听数从", calcator.shanten, "变为", new_calcator.shanten)

    print("遍历所有可以打出的牌，计算如果打出了这张牌，新的向听数将会是多少。（如果新的向听数不增加，则这张打出的牌是不想要的牌）")

    for t in BasicFormShanten.TILE_LIST:
        if t not in hand:
            continue
        new_hand = list(hand)
        new_hand.remove(t)
        new_hand = tuple(new_hand)
        new_calcator = BasicFormShanten(packs, new_hand, rest_tiles)
        new_calcator.run()
        print("打", t, "，向听数从", calcator.shanten, "变为", new_calcator.shanten)
