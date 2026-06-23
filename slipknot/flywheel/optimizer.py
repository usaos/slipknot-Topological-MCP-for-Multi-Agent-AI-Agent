"""
进化飞轮（Evolution Flywheel）
基于贝叶斯优化的自调参系统
Agent 回传业务 Reward，系统自动迭代 TDA 超参数
形成「数据越多，越精准」的正向飞轮
"""
import json
from skopt import gp_minimize
from skopt.space import Real, Integer
from slipknot.flywheel.filter import RewardFilter


class EvolutionFlywheel:
    """
    进化飞轮核心类
    - 接收各行业Agent的Reward反馈
    - 基于高斯过程的贝叶斯优化自动调参
    - 按行业隔离最优参数
    """

    def __init__(self, storage):
        self.storage = storage
        self.filter = RewardFilter()

        # 超参数搜索空间
        self.space = [
            Real(0.01, 0.5, name="hole_threshold"),      # 孔洞持续度阈值
            Integer(5, 50, name="n_neighbors"),          # UMAP近邻数
            Real(0.01, 0.3, name="min_dist"),            # UMAP最小距离
            Real(0.2, 1.0, name="consensus_threshold")   # 共识判定阈值
        ]

        # 默认参数
        self.default_params = {
            "hole_threshold": 0.1,
            "n_neighbors": 15,
            "min_dist": 0.1,
            "consensus_threshold": 0.5
        }

    def _get_history_key(self, industry: str) -> str:
        return f"flywheel:history:{industry}"

    def _get_best_key(self, industry: str) -> str:
        return f"flywheel:best:{industry}"

    def record_reward(self, agent_id: str, industry: str, raw_reward: float, params: dict):
        """
        记录Agent回传的Reward
        积累到一定数量后自动触发贝叶斯优化
        """
        # 获取历史数据
        hist_key = self._get_history_key(industry)
        history = self.storage.get_cache(hist_key) or []

        # 清洗Reward
        reward_list = [item["reward"] for item in history]
        clean_reward = self.filter.clean(raw_reward, reward_list)

        # 保存记录
        history.append({
            "agent_id": agent_id,
            "reward": clean_reward,
            "params": params
        })
        self.storage.set_cache(hist_key, history)

        # 写入审计日志
        self.storage.write_log("reward_feedback", {
            "agent_id": agent_id,
            "industry": industry,
            "raw_reward": raw_reward,
            "clean_reward": clean_reward,
            "params": params
        })

        # 每积累50条且不少于10条时触发优化
        if len(history) >= 10 and len(history) % 50 == 0:
            self._optimize(industry, history)

        return clean_reward

    def _optimize(self, industry: str, history: list):
        """
        执行贝叶斯优化，寻找最优超参数
        使用高斯过程作为代理模型
        """
        # 准备训练数据
        X = []
        y = []
        for item in history:
            p = item["params"]
            xi = [
                p.get("hole_threshold", self.default_params["hole_threshold"]),
                p.get("n_neighbors", self.default_params["n_neighbors"]),
                p.get("min_dist", self.default_params["min_dist"]),
                p.get("consensus_threshold", self.default_params["consensus_threshold"])
            ]
            X.append(xi)
            y.append(-item["reward"])  # 最小化负Reward = 最大化Reward

        # 高斯过程代理模型目标函数
        def objective(x):
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import Matern
            gp = GaussianProcessRegressor(
                kernel=Matern(),
                random_state=42,
                normalize_y=True
            )
            gp.fit(X, y)
            pred = gp.predict([x])
            return float(pred[0])

        # 执行贝叶斯优化
        try:
            res = gp_minimize(
                objective,
                self.space,
                n_calls=15,
                random_state=42,
                verbose=False
            )

            best_params = {
                "hole_threshold": float(res.x[0]),
                "n_neighbors": int(res.x[1]),
                "min_dist": float(res.x[2]),
                "consensus_threshold": float(res.x[3])
            }

            # 保存最优参数
            best_key = self._get_best_key(industry)
            self.storage.set_cache(best_key, best_params)

            # 记录优化事件
            self.storage.write_log("flywheel_optimize", {
                "industry": industry,
                "sample_count": len(history),
                "best_params": best_params,
                "best_score": -float(res.fun)
            })

            return best_params

        except Exception as e:
            # 优化失败不影响主流程
            self.storage.write_log("flywheel_error", {
                "industry": industry,
                "error": str(e)
            })
            return None

    def get_best_params(self, industry: str) -> dict:
        """
        获取指定行业的最优参数
        无历史数据时返回默认参数
        """
        best_key = self._get_best_key(industry)
        params = self.storage.get_cache(best_key)
        if params:
            return params
        return self.default_params.copy()
