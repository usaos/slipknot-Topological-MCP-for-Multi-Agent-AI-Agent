"""
简单任务池模块
使用 Python 内置 ThreadPoolExecutor 实现异步任务
替代重型 Celery，满足单机部署场景需求
"""
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any


class SimpleTaskPool:
    """
    简单线程池任务调度器
    - 支持提交异步任务
    - 支持查询任务状态
    - 自动管理线程池生命周期
    """

    def __init__(self, max_workers: int = 4):
        self.pool = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks = {}
        self._task_counter = 0

    def submit(self, func: Callable, *args, **kwargs) -> Future:
        """
        提交异步任务
        返回 Future 对象，可通过 .result() 获取结果
        """
        future = self.pool.submit(func, *args, **kwargs)
        self._task_counter += 1
        self._tasks[self._task_counter] = future
        return future

    def get_task_status(self, task_id: int) -> str:
        """查询任务状态"""
        if task_id not in self._tasks:
            return "NOT_FOUND"
        future = self._tasks[task_id]
        if future.done():
            if future.exception():
                return "FAILED"
            return "COMPLETED"
        return "RUNNING"

    def get_task_result(self, task_id: int, timeout: float = None) -> Any:
        """获取任务结果"""
        if task_id not in self._tasks:
            return None
        future = self._tasks[task_id]
        try:
            return future.result(timeout=timeout)
        except Exception:
            return None

    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        self.pool.shutdown(wait=wait)
