"""
存储后端模块
双模式自动降级：
1. InMemoryBackend - 本地开发模式，零中间件依赖
2. RedisBackend - 生产模式，可选接入
无Redis时自动降级为内存存储
"""
import json
import os
from datetime import datetime


class InMemoryBackend:
    """
    内存存储后端
    用于本地开发、单机部署场景
    无需任何外部中间件
    """

    def __init__(self):
        self.cache = {}

    def set_cache(self, key: str, data: dict, ttl: int = 86400):
        """设置缓存（内存模式下ttl仅作标记，不自动过期）"""
        self.cache[key] = data

    def get_cache(self, key: str):
        """获取缓存"""
        return self.cache.get(key)

    def delete_cache(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]

    def write_log(self, log_type: str, content: dict):
        """
        写入审计日志
        本地模式：写入 slipknot_audit.log 文件
        """
        log = {
            "time": str(datetime.now()),
            "type": log_type,
            "data": content
        }
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "..",
            "slipknot_audit.log"
        )
        # 简化路径，直接写在项目根目录
        log_path = "slipknot_audit.log"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
        except Exception:
            # 日志写入失败不影响主流程
            pass


# Redis 可选后端（未安装redis库时为None）
try:
    import redis

    class RedisBackend(InMemoryBackend):
        """
        Redis 存储后端
        用于生产环境、多实例部署场景
        支持分布式缓存共享
        """

        def __init__(self, host: str = "localhost", port: int = 6379, db: int = 1):
            self.r = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=False
            )

        def set_cache(self, key: str, data: dict, ttl: int = 86400):
            """设置缓存，带过期时间"""
            self.r.setex(key, ttl, json.dumps(data))

        def get_cache(self, key: str):
            """获取缓存"""
            raw = self.r.get(key)
            return json.loads(raw) if raw else None

        def delete_cache(self, key: str):
            """删除缓存"""
            self.r.delete(key)

except ImportError:
    RedisBackend = None


def get_storage():
    """
    工厂函数：自动选择存储后端
    环境变量 USE_REDIS=1 时启用Redis，否则使用内存存储
    """
    if RedisBackend and os.getenv("USE_REDIS", "0") == "1":
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        return RedisBackend(host=host, port=port)
    return InMemoryBackend()
