"""
拓扑状态数据模型
使用 Pydantic 替代 Protobuf，简化序列化流程
"""
from pydantic import BaseModel
from typing import List


class PersistencePoint(BaseModel):
    """持久图上的单个点"""
    birth: float
    death: float
    pers: float


class TopologyState(BaseModel):
    """
    Agent 拓扑状态向量
    用于 A2A 通信和仲裁法庭输入
    """
    agent_id: str
    h1: List[PersistencePoint]
    confidence: float
