"""
Reward 异常过滤器
防止恶意Agent或异常数据污染自进化飞轮
"""
import numpy as np


class RewardFilter:
    """
    Reward 数据清洗过滤器
    1. 极值截断：限制Reward上下界
    2. 滑动均值异常检测：剔除偏离历史分布过大的异常值
    """

    def __init__(self, clip_min: float = -10.0, clip_max: float = 10.0):
        self.clip_min = clip_min
        self.clip_max = clip_max

    def clean(self, reward: float, history: list) -> float:
        """
        清洗Reward数据
        :param reward: 原始Reward值
        :param history: 历史Reward列表
        :return: 清洗后的Reward值
        """
        # 第一步：极值截断
        r = np.clip(reward, self.clip_min, self.clip_max)

        # 第二步：历史数据不足时直接返回截断值
        if len(history) < 20:
            return float(r)

        # 第三步：3σ 异常检测，偏离过大则用均值替代
        recent_history = history[-20:]
        mean_h = np.mean(recent_history)
        std_h = np.std(recent_history)

        if std_h > 0 and abs(r - mean_h) > 3 * std_h:
            return float(mean_h)

        return float(r)
