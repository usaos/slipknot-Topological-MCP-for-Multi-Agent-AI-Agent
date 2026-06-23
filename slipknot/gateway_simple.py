"""
Slipknot V4.1 Lite MCP 网关 - 纯FastAPI版本
不依赖mcp库，直接用FastAPI实现MCP工具调用接口
四大核心能力：
1. TDA拓扑分析
2. 行业自适应业务提示
3. 多Agent拓扑共识仲裁
4. Reward自进化飞轮
"""
import json
import hashlib
import os
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

from slipknot.core.engine import SlipknotTDAEngine
from slipknot.consensus.court import ConsensusCourt
from slipknot.consensus.models import TopologyState
from slipknot.flywheel.optimizer import EvolutionFlywheel
from slipknot.storage.backend import get_storage
from slipknot.task.pool import SimpleTaskPool
from slipknot.plugins import energy, quant, fraud

# ========== 全局单例初始化 ==========
storage = get_storage()
task_pool = SimpleTaskPool(max_workers=int(os.getenv("MAX_WORKERS", "4")))
court = ConsensusCourt()
flywheel = EvolutionFlywheel(storage)

# 安全沙箱：允许读取的目录白名单
ALLOW_PATH = [
    "/data/safe_zone/",
    "./tmp/",
    "tmp/",
    os.path.abspath("./tmp") + "/"
]

# Agent 鉴权 Token（生产环境应从配置/数据库读取）
VALID_TOKEN = os.getenv("AGENT_TOKEN", "enterprise-agent-key-2026")

# ========== FastAPI 应用 ==========
app = FastAPI(title="Slipknot V4.1 Lite - 轻量拓扑仲裁MCP协处理器")


# ========== 请求模型 ==========
class MCPRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


# ========== 鉴权工具函数 ==========
def check_token(auth: Optional[str] = None):
    """简单Token鉴权"""
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    token = auth.replace("Bearer ", "").strip()
    if token != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Agent Token")
    return True


def check_sandbox(file_path: str) -> bool:
    """检查文件路径是否在安全沙箱内"""
    abs_path = os.path.abspath(file_path)
    for allowed in ALLOW_PATH:
        abs_allowed = os.path.abspath(allowed)
        if abs_path.startswith(abs_allowed):
            return True
    return False


# ========== MCP 工具实现 ==========
def submit_tda_tool(csv_path: str, industry: str = "general") -> dict:
    """
    提交拓扑数据分析任务
    输入：CSV文件路径、行业类型
    输出：任务状态 + data_id（用于后续查询结果）
    """
    # 安全沙箱校验
    if not check_sandbox(csv_path):
        return {"error": "文件路径超出安全沙箱范围", "code": "SANDBOX_VIOLATION"}

    # 文件存在性校验
    if not Path(csv_path).exists():
        return {"error": "文件不存在", "code": "FILE_NOT_FOUND"}

    # 生成 data_id（基于文件路径+修改时间，确保缓存一致性）
    mtime = Path(csv_path).stat().st_mtime
    data_id = hashlib.md5(f"{csv_path}:{mtime}".encode()).hexdigest()

    # 缓存命中直接返回
    cache_key = f"tda:{data_id}"
    if storage.get_cache(cache_key):
        return {
            "status": "cached",
            "data_id": data_id,
            "message": "拓扑结果已缓存，可直接查询"
        }

    # 获取该行业最优参数
    best_params = flywheel.get_best_params(industry)

    # 异步提交TDA计算任务
    def calc_task():
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            # 仅保留数值列，去除空值
            num_data = df.select_dtypes(include="number").dropna().values
            if len(num_data) == 0:
                return {"error": "CSV文件中无数值列", "code": "NO_NUMERIC_DATA"}
            engine = SlipknotTDAEngine(best_params)
            result = engine.fit(num_data)
            result["industry"] = industry
            result["params_used"] = best_params
            storage.set_cache(cache_key, result, ttl=86400)
            return result
        except Exception as e:
            return {"error": str(e), "code": "CALCULATION_ERROR"}

    task_pool.submit(calc_task)

    return {
        "status": "processing",
        "data_id": data_id,
        "message": "拓扑分析任务已提交，稍后通过 get_insight 查询结果"
    }


def get_insight_tool(data_id: str, x_agent_role: str = "general") -> dict:
    """
    获取拓扑分析结果与行业专属操作指令
    输入：data_id
    输出：业务洞察 + 操作指令 + 原始拓扑数据
    """
    cache_key = f"tda:{data_id}"
    result = storage.get_cache(cache_key)
    if not result:
        return {
            "status": "pending",
            "message": "计算尚未完成，请稍后重试"
        }

    h1_count = result.get("h1_count", 0)
    h0_count = result.get("h0_count", 0)

    # 根据Agent角色匹配行业插件
    role_lower = x_agent_role.lower()
    if "energy" in role_lower or "storage" in role_lower:
        tip = energy.get_energy_tip(h1_count, h0_count)
        industry = "energy"
    elif "quant" in role_lower or "trade" in role_lower or "finance" in role_lower:
        tip = quant.get_quant_tip(h1_count, h0_count)
        industry = "quant"
    elif "fraud" in role_lower or "risk" in role_lower:
        tip = fraud.get_fraud_tip(h1_count, h0_count)
        industry = "fraud"
    else:
        tip = f"📊 拓扑分析结果：H1孔洞数量 {h1_count}，H0连通域 {h0_count} 个"
        industry = "general"

    # 获取当前行业最优参数
    best_params = flywheel.get_best_params(industry)

    return {
        "status": "success",
        "insight": tip,
        "topology_summary": {
            "h1_count": h1_count,
            "h0_count": h0_count,
            "singularity_count": len(result.get("singularities", []))
        },
        "best_params": best_params,
        "raw_data": result
    }


def arbitrate_tool(state_a: dict, state_b: dict) -> dict:
    """
    多Agent拓扑共识仲裁
    输入：两个Agent的拓扑状态（agent_id, h1, confidence）
    输出：仲裁判决 + 距离度量 + 弱势Agent标识
    """
    try:
        s_a = TopologyState(**state_a)
        s_b = TopologyState(**state_b)
    except Exception as e:
        return {"error": f"拓扑状态格式错误: {str(e)}", "code": "INVALID_STATE"}

    # 执行仲裁
    verdict = court.arbitrate(s_a, s_b)

    # 写入审计日志
    storage.write_log("arbitration", {
        "agent_a": state_a.get("agent_id"),
        "agent_b": state_b.get("agent_id"),
        "verdict": verdict
    })

    return verdict


def send_reward_tool(agent_id: str, industry: str, reward: float, params: dict) -> dict:
    """
    回传业务Reward，驱动自进化飞轮
    输入：Agent ID、行业、Reward值、使用的参数
    输出：记录状态
    """
    clean_reward = flywheel.record_reward(agent_id, industry, reward, params)
    return {
        "status": "success",
        "clean_reward": clean_reward,
        "message": "Reward已记录，参数将持续自动优化"
    }


# ========== MCP 工具路由 ==========
TOOL_MAP = {
    "submit_tda": submit_tda_tool,
    "get_insight": get_insight_tool,
    "arbitrate": arbitrate_tool,
    "send_reward": send_reward_tool,
}


@app.post("/mcp")
async def mcp_endpoint(
    request: MCPRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_agent_role: Optional[str] = Header("general", alias="X-Agent-Role")
):
    """MCP 工具调用统一入口"""
    # 鉴权
    check_token(authorization)

    # 查找工具
    tool_name = request.name
    if tool_name not in TOOL_MAP:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    tool_func = TOOL_MAP[tool_name]

    # 调用工具（注入header参数）
    args = request.arguments.copy()
    if tool_name == "get_insight":
        args["x_agent_role"] = x_agent_role

    result = tool_func(**args)
    return result


# ========== 健康检查接口 ==========
@app.get("/health")
async def health_check():
    """服务健康检查"""
    return {
        "status": "ok",
        "version": "4.1.0-lite",
        "storage_type": type(storage).__name__,
        "workers": int(os.getenv("MAX_WORKERS", "4"))
    }


# ========== 工具列表接口 ==========
@app.get("/mcp/tools")
async def list_tools():
    """列出所有可用的MCP工具"""
    return {
        "tools": [
            {
                "name": "submit_tda",
                "description": "提交拓扑数据分析任务，输入CSV文件路径和行业类型，返回data_id",
                "parameters": {
                    "csv_path": "string - CSV文件路径",
                    "industry": "string - 行业类型（energy/quant/fraud/general），默认general"
                }
            },
            {
                "name": "get_insight",
                "description": "获取拓扑分析结果与行业专属操作指令",
                "parameters": {
                    "data_id": "string - 任务ID"
                }
            },
            {
                "name": "arbitrate",
                "description": "多Agent拓扑共识仲裁，输入两个Agent的拓扑状态",
                "parameters": {
                    "state_a": "dict - Agent A的拓扑状态（agent_id, h1, confidence）",
                    "state_b": "dict - Agent B的拓扑状态（agent_id, h1, confidence）"
                }
            },
            {
                "name": "send_reward",
                "description": "回传业务Reward，驱动自进化飞轮",
                "parameters": {
                    "agent_id": "string - Agent ID",
                    "industry": "string - 行业类型",
                    "reward": "float - Reward值",
                    "params": "dict - 使用的TDA参数"
                }
            }
        ]
    }
