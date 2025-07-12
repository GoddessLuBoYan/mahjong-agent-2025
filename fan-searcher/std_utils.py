""" 使用python模仿c++ std的部分实现 """


def std_includes(main_list, sub_list):
    """ 要求main_list和sub_list均为相同顺序排序的列表，或其它可index的东西 """
    idx2 = 0
    end_idx2 = len(sub_list)
    idx1 = 0
    end_idx1 = len(main_list)
    while idx2 != end_idx2:
        if idx1 == end_idx1 or sub_list[idx2] < main_list[idx1]:
            return False
        if not (main_list[idx1] < sub_list[idx2]):
            idx2 += 1
        idx1 += 1
    return True


def _test_std_includes():
    v1 = 'abcfhx'
    v2 = 'abc'
    v3 = 'ac'
    v4 = 'aab'
    v5 = 'g'
    v6 = 'acg'
    # v7 = 'ABC'  # c++中，std::includes可以传入对大小写不敏感的比较函数key函数，但此特性我暂不需要，所以不评测此用例
    
    assert std_includes(v1, v2)
    assert std_includes(v1, v3)
    assert not std_includes(v1, v4)
    assert not std_includes(v1, v5)
    assert not std_includes(v1, v6)


def _test():
    _test_std_includes()


if __name__ == '__main__':
    _test()
