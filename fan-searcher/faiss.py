import numpy as np

class SimpleFAISS:
    """ 在100w条数据这个量级，完全没有问题 """

    def __init__(self, p_hu_array):
        self.p_hu_array = p_hu_array
    
    @classmethod
    def distance(cls, p_hu_array, p_hand_array):
        x = p_hu_array[:, 2:36] - p_hand_array[:, 2:36]  # 手牌比目标多的为负，不参与距离计算；手牌比目标少的为正，参与距离计算，相当于向听
        distance = np.sum(x + np.abs(x), axis=1) / 2
        return distance

    def search(self, p_hand):

        # p_hand_array = np.tile(p_hand, (self.p_hu_array.shape[0], 1))
        p_hand_array = np.broadcast_to(p_hand, (self.p_hu_array.shape[0], p_hand.shape[0]))

        distances = self.distance(self.p_hu_array, p_hand_array)

        # 返回前k个
        return distances.argsort()

    def search_return_distance(self, p_hand, topk):

        # p_hand_array = np.tile(p_hand, (self.p_hu_array.shape[0], 1))
        p_hand_array = np.broadcast_to(p_hand, (self.p_hu_array.shape[0], p_hand.shape[0]))

        distances = self.distance(self.p_hu_array, p_hand_array)

        # 返回前k个
        args = distances.argsort()[:topk]
        return [(i, distances[i]) for i in args]

