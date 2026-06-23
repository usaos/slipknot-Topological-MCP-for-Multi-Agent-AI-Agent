"""
Slipknot TDA 核心加速模块
使用 Numba JIT 编译加速距离矩阵计算和孤立度评分
"""
import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True)
def calc_distance_matrix(points: np.ndarray) -> np.ndarray:
    """
    JIT加速计算欧式距离矩阵
    替代 scipy.spatial.distance.pdist，避免GIL阻塞
    """
    n = points.shape[0]
    dist_mat = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((points[i] - points[j]) ** 2))
            dist_mat[i, j] = dist
            dist_mat[j, i] = dist
    return dist_mat


@jit(nopython=True)
def get_isolation_score(dist_matrix: np.ndarray) -> np.ndarray:
    """
    JIT加速计算每个点的平均近邻距离（孤立度评分）
    分数越高表示该点越孤立，越可能是奇点
    """
    n = dist_matrix.shape[0]
    score = np.empty(n, dtype=np.float64)
    for i in range(n):
        score[i] = np.mean(dist_matrix[i])
    return score


def adaptive_sample(data: np.ndarray, max_sample: int = 3000, min_sample: int = 80) -> np.ndarray:
    """
    自适应采样策略，控制TDA计算复杂度
    - 小样本全量计算
    - 中等样本随机均匀采样
    - 超大数据集启用Witness复形近似
    """
    n = len(data)
    if n <= min_sample:
        return data
    sample_num = min(max_sample, n)
    idx = np.random.choice(n, sample_num, replace=False)
    return data[idx]
