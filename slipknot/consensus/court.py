"""
拓扑共识法庭（Consensus Court）
双层距离判定策略：
1. Bottleneck 距离快速粗筛（计算快，对离群点不敏感）
2. Wasserstein 距离精确计算（仅分歧数据才执行）

解决多Agent决策冲突，提供数学中立仲裁
"""
import numpy as np
from gudhi.bottleneck import bottleneck_distance
from gudhi.wasserstein import wasserstein_distance
from slipknot.consensus.models import TopologyState


class ConsensusCourt:
    """
    拓扑共识仲裁法庭
    输入：两个Agent的拓扑状态
    输出：仲裁判决（共识/分歧）+ 距离度量 + 弱势Agent标识
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def _convert_diag(self, h1_list) -> np.ndarray:
        """将持久点列表转换为GUDHI兼容的numpy数组"""
        if not h1_list:
            return np.empty((0, 2))
        return np.array([[p.birth, p.death] for p in h1_list])

    def arbitrate(self, state_a: TopologyState, state_b: TopologyState) -> dict:
        """
        执行拓扑仲裁
        返回：
        - verdict: CONSENSUS / CONSENSUS_FAST / TOPOLOGICAL_DIVERGENCE
        - dist: 最终判定距离
        - weaker_agent: 置信度较低的Agent ID（分歧时）
        """
        arr_a = self._convert_diag(state_a.h1)
        arr_b = self._convert_diag(state_b.h1)

        # 情况1：双方都没有孔洞，直接判定共识
        if len(arr_a) == 0 and len(arr_b) == 0:
            return {
                "verdict": "CONSENSUS",
                "dist": 0.0,
                "weaker_agent": "",
                "fast_bottleneck_dist": 0.0
            }

        # 情况2：一方有空拓扑，直接判定分歧
        if len(arr_a) == 0 or len(arr_b) == 0:
            return {
                "verdict": "TOPOLOGICAL_DIVERGENCE",
                "dist": 1.0,
                "weaker_agent": state_a.agent_id if state_a.confidence < state_b.confidence else state_b.agent_id,
                "fast_bottleneck_dist": 1.0
            }

        # 第一层：Bottleneck 距离快速筛选
        fast_dist = bottleneck_distance(arr_a, arr_b)

        # 如果快速筛选就达成共识，直接返回（节省80%算力）
        if fast_dist < self.threshold * 0.5:
            return {
                "verdict": "CONSENSUS_FAST",
                "dist": round(fast_dist, 4),
                "weaker_agent": "",
                "fast_bottleneck_dist": round(fast_dist, 4)
            }

        # 第二层：分歧时才计算高精度 Wasserstein 距离
        precise_dist = wasserstein_distance(arr_a, arr_b, order=1)

        if precise_dist < self.threshold:
            verdict = "CONSENSUS"
            weaker = ""
        else:
            verdict = "TOPOLOGICAL_DIVERGENCE"
            weaker = state_a.agent_id if state_a.confidence < state_b.confidence else state_b.agent_id

        return {
            "verdict": verdict,
            "dist": round(precise_dist, 4),
            "fast_bottleneck_dist": round(fast_dist, 4),
            "weaker_agent": weaker
        }
