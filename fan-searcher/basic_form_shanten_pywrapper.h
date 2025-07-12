#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "vector"
#include "unordered_map"
#include "string"
#include "unordered_set"
#include <algorithm>
#include <tuple>

using namespace std;
using Tile = string;
using Pack = vector<Tile>;
using TileTable = unordered_map<Tile, int>;

// from cpp
using Tile = string;
tuple<vector<tuple<Tile, bool, bool>>, vector<Tile>> getXiantenBasic(vector<Pack>& packs, vector<Tile>& hand, TileTable& restTiles);


static PyObject*
getXiantenBasicPyWrapper(PyObject *self, PyObject *args, PyObject *kwargs) {
    static char *kwlist[] = {const_cast<char*>("packs"), const_cast<char*>("hand"), const_cast<char*>("restTiles"), nullptr};
    PyObject *packs_py = nullptr;
    PyObject *hand_py = nullptr;
    PyObject *restTiles_py = nullptr;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOO", kwlist, &packs_py, &hand_py, &restTiles_py)) {
        return nullptr;
    }
    if (!PyTuple_Check(packs_py)) {
        PyErr_SetString(PyExc_TypeError, "packs must be tuple[tuple[str]]");
        return nullptr;
    }
    if (!PyTuple_Check(hand_py)) {
        PyErr_SetString(PyExc_TypeError, "hand must be tuple[str]");
        return nullptr;
    }
    if (!PyDict_Check(restTiles_py)) {
        PyErr_SetString(PyExc_TypeError, "rest_tiles must be dict[str, int]");
        return nullptr;
    }

    uint64_t packsSize = (uint64_t)PyTuple_Size(packs_py);
    vector<Pack> packs;
    packs.reserve(packsSize);
    for (int i = 0; i < packsSize; i++) {
        PyObject *pack_py = PyTuple_GET_ITEM(packs_py, i);
        if (!PyTuple_Check(pack_py)) {
            PyErr_SetString(PyExc_TypeError, "all pack in packs must be tuple[str]");
            return nullptr;
        }
        Pack pack;
        int packSize = PyTuple_Size(pack_py);
        for (int j = 0; j < packSize; j++) {
            PyObject *tile_py = PyTuple_GET_ITEM(pack_py, j);
            if (!PyUnicode_Check(tile_py)) {
                PyErr_SetString(PyExc_TypeError, "all tile in pack (pack in packs) must be str");
                return nullptr;
            }
            const char* c_str = PyUnicode_AsUTF8(tile_py);
            if (!c_str) {
                PyErr_SetString(PyExc_RuntimeError, "parse tile failed");
                return nullptr;
            }
            pack.push_back(Tile{c_str});
        }
        packs.push_back(pack);
    }

    uint64_t handSize = (uint64_t)PyTuple_Size(hand_py);
    vector<Tile> hand;
    hand.reserve(handSize);
    for (int i = 0; i < handSize; i++) {
        PyObject *tile_py = PyTuple_GET_ITEM(hand_py, i);
        if (!PyUnicode_Check(tile_py)) {
            PyErr_SetString(PyExc_TypeError, "all tile in hand must be str");
            return nullptr;
        }
        const char* c_str = PyUnicode_AsUTF8(tile_py);
        if (!c_str) {
            PyErr_SetString(PyExc_RuntimeError, "parse tile failed");
            return nullptr;
        }
        hand.push_back(Tile{c_str});
    }

    TileTable restTiles;

    PyObject *key, *value;
    Py_ssize_t pos = 0;
 
    while (PyDict_Next(restTiles_py, &pos, &key, &value)) {
        // 确保键是 Unicode 字符串
        if (!PyUnicode_Check(key)) {
            PyErr_SetString(PyExc_TypeError, "all key in restTiles must be str!");
            return nullptr;
        }
 
        // 确保值是长整型
        if (!PyLong_Check(value)) {
            PyErr_SetString(PyExc_TypeError, "all value in restTiles must be int!");
            return nullptr;
        }
 
        // 将键转换为 std::string
        const char *c_key = PyUnicode_AsUTF8(key);
        if (!c_key) {
            continue; // 或者抛出异常，取决于需求
        }
        std::string key_str(c_key);
 
        // 将值转换为 int
        int value_int = PyLong_AsLong(value);
 
        // 将键值对插入到 unordered_map 中
        restTiles[key_str] = value_int;
    }

    auto result = getXiantenBasic(packs, hand, restTiles);

    const auto& restTilesWithInfo = std::get<0>(result);
    const auto& restHand = std::get<1>(result);
 
    // 创建 Python 列表来保存转换后的结果
    PyObject* pyResult = PyTuple_New(2);
 
    // 转换第一个向量：vector<tuple<string, bool, bool>>
    PyObject* restTilesWithInfo_py = PyTuple_New(restTilesWithInfo.size());
    for (size_t i = 0; i < restTilesWithInfo.size(); ++i) {
        const auto& info = restTilesWithInfo[i];
        const std::string& str = std::get<0>(info);
        bool b1 = std::get<1>(info);
        bool b2 = std::get<2>(info);
 
        // 创建内部元组
        PyObject* info_py = PyTuple_New(3);
        PyTuple_SetItem(info_py, 0, PyUnicode_FromString(str.c_str()));
        PyTuple_SetItem(info_py, 1, PyBool_FromLong(b1));
        PyTuple_SetItem(info_py, 2, PyBool_FromLong(b2));
 
        PyTuple_SetItem(restTilesWithInfo_py, i, info_py);
    }
 
    // 转换第二个向量：vector<string>
    PyObject* restHand_py = PyTuple_New(restHand.size());
    for (size_t i = 0; i < restHand.size(); ++i) {
        const Tile& str = restHand[i];
        PyTuple_SetItem(restHand_py, i, PyUnicode_FromString(str.c_str()));
    }
 
    // 将转换后的对象放入结果元组中
    PyTuple_SetItem(pyResult, 0, restTilesWithInfo_py);
    PyTuple_SetItem(pyResult, 1, restHand_py);
 
    return pyResult;
}

static const char* BasicFormShantenDoc = \
"get_xianten_basic(packs: tuple[tuple[str, ...], ...], hand: tuple[str, ...], rest_tiles: dict[str, int]) -> tuple[tuple[str, int, int], ...], tuple[str]";

// 定义模块的方法列表
static PyMethodDef BasicFormShantenMethods[] = {
    {"get_xianten_basic", (PyCFunction)getXiantenBasicPyWrapper, METH_VARARGS | METH_KEYWORDS, "Calculate basic form shanten."},
    {NULL, NULL, 0, NULL}  // 哨兵值，表示方法列表结束
};
 
// 定义模块的结构
static struct PyModuleDef basicformshantenmodule = {
    PyModuleDef_HEAD_INIT,
    "BasicFormShanten",  // 模块名称
    NULL,               // 模块文档字符串
    -1,                 // 模块保持全局状态
    BasicFormShantenMethods
};
 
// 模块初始化函数
PyMODINIT_FUNC PyInit_BasicFormShanten(void) {
    return PyModule_Create(&basicformshantenmodule);
}