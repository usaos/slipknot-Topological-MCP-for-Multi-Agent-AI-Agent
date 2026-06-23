"""
Slipknot TDA 核心计算引擎
整合 UMAP 降维、持久同调计算、奇点识别
"""
import numpy as np
from ripser import ripser
from slipknot.core.accel import calc_distance_matrix, get_isolation_score, adaptive_sample


class SlipknotTDAEngine:
    """
    拓扑数据分析核心引擎
    输入：原始数值数据
    输出：H1持久图、奇点列表、降维嵌入采样
    """

    def __init__(self, params: dict):
        self.params = params
        self.n_neighbors = params.get("n_neighbors", 15)
        self.min_dist = params.get("min_dist", 0.1)
        self.hole_threshold = params.get("hole_threshold", 0.1)
        self.top_k = params.get("top_k", 5)

    def fit(self, raw_data: np.ndarray) -> dict:
        """
        执行完整TDA分析流程
        1. 自适应采样
        2. UMAP降维
        3. 距离矩阵计算 + 奇点识别
        4. 持久同调计算（H0, H1, H2）
        """
        # 自适应采样控制计算量
        data = adaptive_sample(raw_data)

        # UMAP 流形降维
        import umap
        reducer = umap.UMAP(
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            random_state=42
        )
        embed = reducer.fit_transform(data)

        # JIT加速计算距离矩阵 + 孤立度评分
        dist_mat = calc_distance_matrix(embed)
        iso_scores = get_isolation_score(dist_mat)

        # 提取 Top-K 奇点
        singularity_idx = np.argsort(iso_scores)[-self.top_k:][::-1]
        singularities = [
            {"idx": int(i), "score": float(iso_scores[i])}
            for i in singularity_idx
        ]

        # 持久同调计算（支持 H0, H1, H2 多阶拓扑）
        rip_result = ripser(data, maxdim=2)
        dgms = rip_result["dgms"]

        # 提取 H1 一维孔洞（过滤低持续度噪声）
        h1_list = []
        if len(dgms) >= 2:
            for b, d in dgms[1]:
                if d != np.inf and (d - b) > self.hole_threshold:
                    h1_list.append({
                        "birth": float(b),
                        "death": float(d),
                        "pers": float(d - b)
                    })

        # 提取 H0 连通域
        h0_count = 0
        if len(dgms) >= 1:
            h0_count = len([p for p in dgms[0] if p[1] != np.inf])

        return {
            "sample_size": len(data),
            "h0_count": h0_count,
            "h1": h1_list,
            "h1_count": len(h1_list),
            "singularities": singularities,
            "embed_sample": embed[:100].tolist()
        }
