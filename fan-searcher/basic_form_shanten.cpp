#include "vector"
#include "unordered_map"
#include "string"
#include "unordered_set"
#include <algorithm>
#include <tuple>
#include "iostream"
#include "basic_form_shanten_pywrapper.h"

using namespace std;
using Tile = string;
using TileType = char;
using TileNum = int;
using Pack = vector<Tile>;
struct PathUnit;
using WorkPath = vector<PathUnit>;
using WorkState = vector<WorkPath>;

using TileTable = unordered_map<Tile, int>;
using UsefulTable = unordered_map<Tile, int>;

static TileType getTileType(Tile t) {
    return t[0];
}

static TileNum getTileNum(Tile t) {
    return t[1] - '0';
}

static Tile makeTile(TileType t, TileNum n) {
    string tile;
    tile += t;
    tile += to_string(n);
    return tile;
}

static bool isNumberTile(Tile t) {
    auto type = getTileType(t);
    switch (type) {
        case 'W':
        case 'B':
        case 'T':
            return true;
        default:
            return false;
    }
}

static bool hasNeighbor(TileTable& cntTable, Tile t) {
    if (!isNumberTile(t)) return false;
    auto type = getTileType(t);
    auto num = getTileNum(t);
    if (num > 1 && cntTable[makeTile(type, num - 1)]) {return true;}
    if (num > 2 && cntTable[makeTile(type, num - 2)]) {return true;}
    if (num < 9 && cntTable[makeTile(type, num + 1)]) {return true;}
    if (num < 8 && cntTable[makeTile(type, num + 2)]) {return true;}
    return false;
}


enum UnitType {
    CHI = 1,
    PENG = 2,
    PAIR = 4,
    CHI_OPEN_END = 5,
    CHI_CLOSED = 6,
    INCOMPLETE_PENG = 7
};

static std::string to_string(UnitType ut) {
    switch (ut) {
        case UnitType::CHI:
            return "CHI";
        case UnitType::PENG:
            return "PENG";
        case UnitType::PAIR:
            return "PAIR";
        case UnitType::CHI_OPEN_END:
            return "CHI_OPEN_END";
        case UnitType::CHI_CLOSED:
            return "CHI_CLOSED";
        case UnitType::INCOMPLETE_PENG:
            return "INCOMPLETE_PENG";
        default:
            return "Unknown";
    }
}

struct PathUnit {
public:
    //PathUnit () {}
    PathUnit(UnitType unitType, vector<Tile> unit) : unitType(unitType), unit(unit), wantedTile("X0") {}
    PathUnit(UnitType unitType, vector<Tile> unit, Tile wantedTile) : unitType(unitType), unit(unit), wantedTile(wantedTile) {}

    string toString() {
        string res{to_string(unitType)};
        res += "{";
        for (int i = 0; i < unit.size(); i++) {
            res += unit[i];
        }
        if (wantedTile != "X0") {
            res += "[[" + wantedTile + "]]";
        }
        res += "}";
        return res;
    }

    bool operator < (const PathUnit& other) const {
        if (unitType < other.unitType) return false;
        if (unitType > other.unitType) return true;
        if (wantedTile < other.wantedTile) return false;
        if (wantedTile > other.wantedTile) return true;
        if (unit.size() < other.unit.size()) return false;
        if (unit.size() > other.unit.size()) return true;
        for (int i = 0; i < unit.size(); i++) {
            Tile t1 = unit[i];
            Tile t2 = other.unit[i];
            if (t1 < t2) return false;
            if (t1 > t2) return true;
        }
        return false;
    }

    UnitType unitType;
    vector<Tile> unit;
    Tile wantedTile;
};

static Tile TILE_LIST[] = {
    "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", 
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", 
    "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", 
    "F1", "F2", "F3", "F4", "J1", "J2", "J3"
};

class BasicFormShanten { 
public:
    BasicFormShanten(vector<Pack> packs, vector<Tile> hand, TileTable restTiles) : packs(packs), hand(hand), restTiles(restTiles) {
        packCnt = packs.size();
        for (auto& tile : TILE_LIST) {
            cntTable[tile] = 0;
            if (restTiles.find(tile) == restTiles.end()) {
                restTiles[tile] = 0;
            }
        }
        for (auto& tile: hand) {
            cntTable[tile]++;
        }
    }

    int run() {
        this->shanten = this->walk();
        return this->shanten;
    }

    bool existsWorkPath() {
        // 复制一份，防止更改workPath本身
        auto workPathCopy = workPath;
        std::sort(workPathCopy.begin(), workPathCopy.end());
        return std::any_of(workState.begin(), workState.end(), [&workPathCopy](auto p){
            return std::includes(p.begin(), p.end(), workPathCopy.begin(), workPathCopy.end());
        });
    }

    void saveWorkPath() {
        // 复制一份，防止更改workPath本身
        auto workPathCopy = workPath;
        std::sort(workPathCopy.begin(), workPathCopy.end());
        workState.push_back(workPathCopy);
    }

    void showWorkPath() {
        if (show) {
            for (auto u : workPath) {
                cout << u.toString() << " ";
            }
            cout << endl;
        }
        
    }

    int walk() {
        // 如果已经有4个副露，那么如果某一张牌有至少两张手牌，就是和了，没有就是听牌
        if (packs.size() == 4) {
            for (auto& t : TILE_LIST) {
                if (cntTable[t] > 1) {
                    return -1;
                }
            }
            return 0;
        }
        // 如果已经组成了4个面子，那么如果有雀头，就是和了，没有就是听牌
        if (packCnt == 4) {
            if (hasPair) {
                return -1;
            }
            return 0;
        }
        
        // 算法说明：
        // 缺少的面子数=4-完成的面子数
        // 缺少的搭子数=缺少的面子数-已有的搭子数
        // 两式合并：缺少的搭子数=4-完成的面子数-已有的搭子数
        int maxRet;
        int incompleteNeed = 4 - packCnt - incompleteCnt;
        if (incompleteNeed > 0) { // 还需要搭子的情况
            // 每个搭子需要1张，每个单张需要2张；如果还没有雀头，那么其中一个单张将用于组雀头，只需要一张
            maxRet = incompleteCnt + incompleteNeed * 2 - (hasPair ? 1 : 0);
        } else { // 搭子齐了的情况
            // 有雀头时，上听数 = 3 - 完成的面子数
            // 无雀头时，上听数 = 4 - 完成的面子数
            maxRet = (hasPair ? 3 : 4) - packCnt;
        }

        int result = maxRet;

        if (packCnt + incompleteCnt > 4) { // 搭子超载
            // 搭子已经足够多了，每个搭子只需要1张即可组成面子，所以搭子数就是向听数
            saveWorkPath();
            return maxRet;
        }

        // 搭子还不足够多，需要遍历所有手牌，尝试组搭子
        // 如果组成了搭子，那么向听数将会因此而减少，否则就不会减少
        for (auto& t : TILE_LIST) {
            // 手里没有这张牌
            if (cntTable[t] < 1) {
                continue;
            }
            auto type = getTileType(t);
            auto num = getTileNum(t);

            // 雀头
            if (!hasPair && cntTable[t] > 1) {
                // 记录雀头
                auto unit = PathUnit(UnitType::PAIR, {t, t});
                workPath.push_back(unit);
                showWorkPath();
                // 还没有记录过这条路径
                if (!existsWorkPath()) {
                    // 削减雀头，递归
                    cntTable[t] -= 2;
                    bool tmp = hasPair;
                    hasPair = true;

                    int ret = walk();
                    result = min(ret, result);

                    // 还原
                    cntTable[t] += 2;
                    hasPair = tmp;
                }
                // 还原
                workPath.pop_back();
            }

            // 刻子
            if (cntTable[t] > 2) {
                // 记录刻子
                auto unit = PathUnit(UnitType::PENG, {t, t, t});
                workPath.push_back(unit);
                showWorkPath();
                // 还没有记录过这条路径
                if (!existsWorkPath()) {
                    // 削减刻子，递归
                    cntTable[t] -= 3;
                    packCnt += 1;

                    int ret = walk();
                    result = min(ret, result);

                    // 还原
                    cntTable[t] += 3;
                    packCnt -= 1;
                }
                // 还原
                workPath.pop_back();
            }

            // 顺子（只能是数字牌，且顺子三张牌均需合法）
            bool isNumber = isNumberTile(t);
            if (isNumber && num <= 7) {
                auto t1 = makeTile(type, num + 1);
                auto t2 = makeTile(type, num + 2);
                if (cntTable[t1] > 0 && cntTable[t2] > 0) {
                    auto unit = PathUnit(UnitType::CHI, {t, t1, t2});
                    workPath.push_back(unit);
                showWorkPath();
                    if (!existsWorkPath()) {
                        // 削减顺子，递归
                        cntTable[t]--;
                        cntTable[t1]--;
                        cntTable[t2]--;
                        packCnt++;

                        int ret = walk();
                        result = min(ret, result);

                        // 还原
                        cntTable[t]++;
                        cntTable[t1]++;
                        cntTable[t2]++;
                        packCnt--;
                    }
                    //还原
                    workPath.pop_back();
                }
            }

            // 如果已经通过削减雀头/面子降低了上听数，再按搭子计算的上听数肯定不会更少
            if (result < maxRet) {
                continue;
            }

            // 刻子搭子
            if (cntTable[t] > 1 && restTiles[t] > 1) {
                // 注意，如果已经组成了刻子，且邻域内没有合法的顺子搭子，则将刻子拆成刻子搭子和单张一定不会减少向听数
                // 也就是，要么是对子，要么邻域内有合法的顺子搭子，二者满足其一即可
                if (cntTable[t] == 2 || hasNeighbor(cntTable, t)) {
                    auto unit = PathUnit(UnitType::INCOMPLETE_PENG, {t, t}, t);
                    workPath.push_back(unit);
                showWorkPath();
                    if (!existsWorkPath()) {
                        // 削减刻子搭子，递归
                        cntTable[t] -= 2;
                        restTiles[t] -= 1;
                        incompleteCnt += 1;

                        int ret = walk();
                        result = min(ret, result);

                        // 还原
                        cntTable[t] += 2;
                        restTiles[t] += 1;
                        incompleteCnt -= 1;
                    }
                    // 还原
                    workPath.pop_back();
                }
            }

            // 顺子搭子（只能是数牌）
            if (isNumber) {
                // 两面或者边张搭子t t+1，显然t不能是9点以上的数牌
                // 先考虑t t+1 t+2这种情况，此时t不能为8点以上的数牌
                if (num < 8) {
                    auto t1 = makeTile(type, num + 1);
                    auto t2 = makeTile(type, num + 2);
                    if (cntTable[t1] > 0 && restTiles[t2] > 0) {
                        // 记录两面或者边张搭子，其中想要的第三张牌牌堆里还有
                        auto unit = PathUnit(UnitType::CHI_OPEN_END, {t, t1}, t2);
                        workPath.push_back(unit);
                showWorkPath();
                        if (!existsWorkPath()) {
                            // 削减顺子搭子，递归
                            cntTable[t]--;
                            cntTable[t1]--;
                            restTiles[t2]--;
                            incompleteCnt++;

                            int ret = walk();
                            result = min(ret, result);

                            // 还原
                            cntTable[t]++;
                            cntTable[t1]++;
                            restTiles[t2]++;
                            incompleteCnt--;
                        }
                        // 还原
                        workPath.pop_back();
                    }
                }

                // 再考虑t t+1 t-1这种情况，此时t不能为9点以上或2点以下的数牌
                if (num < 9 && num > 1) {
                    auto t1 = makeTile(type, num + 1);
                    auto t2 = makeTile(type, num - 1);
                    if (cntTable[t1] > 0 && restTiles[t2] > 0) {
                        // 记录两面或者边张搭子，其中想要的第三张牌牌堆里还有
                        auto unit = PathUnit(UnitType::CHI_OPEN_END, {t, t1}, t2);
                        workPath.push_back(unit);
                showWorkPath();
                        if (!existsWorkPath()) {
                            // 削减顺子搭子，递归
                            cntTable[t]--;
                            cntTable[t1]--;
                            restTiles[t2]--;
                            incompleteCnt++;

                            int ret = walk();
                            result = min(ret, result);

                            // 还原
                            cntTable[t]++;
                            cntTable[t1]++;
                            restTiles[t2]++;
                            incompleteCnt--;
                        }
                        // 还原
                        workPath.pop_back();
                    }
                }

                // 最后考虑坎张的情况
                if (num < 8) {
                    auto t1 = makeTile(type, num + 2);
                    auto t2 = makeTile(type, num + 1);
                    if (cntTable[t1] > 0 && restTiles[t2] > 0) {
                        // 记录坎张搭子，其中想要的第三张牌牌堆里还有
                        auto unit = PathUnit(UnitType::CHI_CLOSED, {t, t1}, t2);
                        workPath.push_back(unit);
                showWorkPath();
                        if (!existsWorkPath()) {
                            // 削减顺子搭子，递归
                            cntTable[t]--;
                            cntTable[t1]--;
                            restTiles[t2]--;
                            incompleteCnt++;

                            int ret = walk();
                            result = min(ret, result);

                            // 还原
                            cntTable[t]++;
                            cntTable[t1]++;
                            restTiles[t2]++;
                            incompleteCnt--;
                        }
                        // 还原
                        workPath.pop_back();
                    }
                }
            }
        }

        // 如果遍历了所有手牌，向听数都没有因此减少
        // 那么现在这种情况就算是当前的最优情况之一了，记录下来
        if (result == maxRet) {
            saveWorkPath();
        }

        return result;
    }
public:
    vector<Pack> packs;
    vector<Tile> hand;
    TileTable restTiles;
    int shanten{20};
    unordered_map<Tile, int> cntTable;
    bool hasPair{false};
    int packCnt{0};
    int incompleteCnt{0};
    WorkPath workPath;
    WorkState workState;
    bool show{false};
};


tuple<vector<tuple<Tile, bool, bool>>, vector<Tile>> getXiantenBasic(vector<Pack>& packs, vector<Tile>& hand, TileTable& restTiles) {
    vector<tuple<Tile, bool, bool>> restTilesWithInfo;
    vector<Tile> restHand;

    auto calculator = BasicFormShanten(packs, hand, restTiles);
    int shanten = calculator.run();

    // 13张牌，仅考虑哪些牌想要即可。手牌中的孤张将不被认为想要。
    if (hand.size() % 3 == 1) {
        // 遍历所有牌，只要我们还能抓到它，就抓一下试试；只要抓它能减少向听数，那么它就是我们想要的牌
        for (auto& tile : TILE_LIST) {
            if (!restTiles[tile]) {
                continue;
            }

            // 跳过孤张字牌和不靠张的数牌，这些牌都无法减少上听数
            if (find(hand.begin(), hand.end(), tile) == hand.end()) {
                if (!hasNeighbor(calculator.cntTable, tile)) {
                    continue;
                }
            }

            auto newHand = hand;
            newHand.push_back(tile);
            restTiles[tile]--;
            auto newCalculator = BasicFormShanten(packs, newHand, restTiles);
            restTiles[tile]++;
            // cout << "parsing tile: " << tile << endl;
            int newShanten = newCalculator.run();
            // cout << tile << ": " << shanten << " vs " << newShanten << endl;
            if (newShanten < shanten) {
                restTilesWithInfo.push_back({
                    tile,
                    any_of(calculator.workState.begin(), calculator.workState.end(), [&tile](WorkPath& workPath){
                        return any_of(workPath.begin(), workPath.end(), [&tile](PathUnit &unit) {
                            return (unit.unitType == UnitType::CHI_OPEN_END || unit.unitType == UnitType::CHI_CLOSED) && unit.wantedTile == tile;
                        });
                    }),
                    any_of(calculator.workState.begin(), calculator.workState.end(), [&tile](WorkPath& workPath){
                        return any_of(workPath.begin(), workPath.end(), [&tile](PathUnit &unit) {
                            // PAIR和INCOMPLETE_PENG等效；注意到PAIR没有wanted_tile，所以改用unit[0]判断
                            return (unit.unitType == UnitType::INCOMPLETE_PENG || unit.unitType == UnitType::PAIR) && unit.unit[0] == tile;
                        });
                    })
                });
            }
        }
    } else { // 14张牌，仅考虑哪些牌不想要即可。当然你想传入15张牌玩大相公我也不算你错
        // 遍历所有手牌，尝试把它打出去。只要向听数不变，就说明它是废牌，就是多余的牌，可以打出去
        auto tileSet = unordered_set<Tile>(hand.begin(), hand.end());
        // cout << tileSet.size() << " " << hand.size() << endl;
        for (auto& tile : tileSet) {
            auto newHand = hand;
            newHand.erase(find(newHand.begin(), newHand.end(), tile));
            auto newCalculator = BasicFormShanten(packs, newHand, restTiles);
            int newShanten = newCalculator.run();
            // cout << tile << ": " << shanten << " vs " << newShanten << endl;
            if (newShanten == shanten) {
                restHand.push_back(tile);
            }
        }
    }
    return make_tuple(restTilesWithInfo, restHand);
}
