"""
Slipknot V4.1 Lite 网关API测试脚本
测试纯FastAPI版本的网关接口
使用方式：
1. 先启动服务：python dev_start.py
2. 再运行测试：python scripts/gateway_test.py
"""
import requests
import json
import time
import os
import sys
import pandas as pd
import numpy as np

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://127.0.0.1:8000/mcp"
HEALTH_URL = "http://127.0.0.1:8000/health"
TOOLS_URL = "http://127.0.0.1:8000/mcp/tools"

HEADERS = {
    "Authorization": "Bearer enterprise-agent-key-2026",
    "Content-Type": "application/json"
}


def generate_test_data():
    """生成测试用的CSV数据"""
    print("📊 生成测试数据...")
    np.random.seed(42)

    # 生成带周期特征的负荷数据（模拟电网负荷）
    n = 500
    t = np.linspace(0, 4 * np.pi, n)
    load1 = 100 + 30 * np.sin(t) + np.random.normal(0, 5, n)
    load2 = 80 + 25 * np.sin(t + 0.5) + np.random.normal(0, 4, n)
    load3 = 120 + 20 * np.sin(t + 1.0) + np.random.normal(0, 3, n)
    temperature = 25 + 10 * np.sin(t / 2) + np.random.normal(0, 2, n)

    df = pd.DataFrame({
        "load_1": load1,
        "load_2": load2,
        "load_3": load3,
        "temperature": temperature,
        "hour": np.arange(n) % 24
    })

    # 保存到tmp目录
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", "grid_load.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"✅ 测试数据已生成：{csv_path}")
    print(f"   数据规模：{len(df)} 行 × {len(df.columns)} 列")
    return csv_path


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "=" * 60)
    print("🏥 测试1：健康检查")
    print("=" * 60)
    try:
        resp = requests.get(HEALTH_URL)
        data = resp.json()
        print(f"✅ 服务状态：{data['status']}")
        print(f"✅ 版本：{data['version']}")
        print(f"✅ 存储类型：{data['storage_type']}")
        print(f"✅ 工作线程：{data['workers']}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败：{e}")
        print("💡 请先启动服务：python dev_start.py")
        return False


def test_tools_list():
    """测试工具列表接口"""
    print("\n" + "=" * 60)
    print("🔧 测试2：工具列表")
    print("=" * 60)
    try:
        resp = requests.get(TOOLS_URL, headers=HEADERS)
        tools = resp.json()
        print(f"✅ 可用工具数量：{len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool.get('description', '')[:50]}...")
        return True
    except Exception as e:
        print(f"❌ 获取工具列表失败：{e}")
        return False


def call_mcp_tool(name: str, arguments: dict, extra_headers: dict = None) -> dict:
    """调用MCP工具"""
    headers = HEADERS.copy()
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "name": name,
        "arguments": arguments
    }
    resp = requests.post(API_URL, json=payload, headers=headers)
    return resp.json()


def test_tda_analysis(csv_path: str):
    """测试TDA拓扑分析"""
    print("\n" + "=" * 60)
    print("📊 测试3：TDA拓扑分析 + 储能行业指令")
    print("=" * 60)

    # 提交任务
    print("\n📤 提交拓扑分析任务...")
    result = call_mcp_tool("submit_tda", {
        "csv_path": csv_path,
        "industry": "energy"
    })
    print(f"   任务状态：{result.get('status')}")
    data_id = result.get("data_id")
    print(f"   data_id：{data_id}")

    # 等待计算完成
    print("\n⏳ 等待计算完成...")
    insight = None
    for i in range(15):
        time.sleep(2)
        insight = call_mcp_tool("get_insight", {"data_id": data_id}, {
            "X-Agent-Role": "energy_storage"
        })
        if insight.get("status") == "success":
            break
        print(f"   等待中... ({i+1}/15) 状态: {insight.get('status')}")

    # 获取结果
    print("\n📋 拓扑分析结果：")
    if insight and insight.get("status") == "success":
        summary = insight.get("topology_summary", {})
        print(f"   H1孔洞数量：{summary.get('h1_count')}")
        print(f"   H0连通域数量：{summary.get('h0_count')}")
        print(f"   奇点数量：{summary.get('singularity_count')}")
        print(f"\n💡 储能调度指令：")
        print(insight.get("insight"))
        print(f"\n⚙️ 当前最优参数：")
        print(json.dumps(insight.get("best_params"), indent=3, ensure_ascii=False))
        return data_id
    else:
        print(f"❌ 计算失败或超时：{insight}")
        return None


def test_consensus_arbitration():
    """测试拓扑共识仲裁"""
    print("\n" + "=" * 60)
    print("⚖️ 测试4：多Agent拓扑共识仲裁")
    print("=" * 60)

    # 场景1：相似拓扑（应该达成共识）
    print("\n🔹 场景1：相似拓扑（预期：共识）")
    state_a = {
        "agent_id": "storage-agent-01",
        "h1": [
            {"birth": 0.1, "death": 0.3, "pers": 0.2},
            {"birth": 0.2, "death": 0.45, "pers": 0.25}
        ],
        "confidence": 0.92
    }
    state_b = {
        "agent_id": "grid-agent-02",
        "h1": [
            {"birth": 0.12, "death": 0.32, "pers": 0.2},
            {"birth": 0.22, "death": 0.47, "pers": 0.25}
        ],
        "confidence": 0.88
    }
    result = call_mcp_tool("arbitrate", {"state_a": state_a, "state_b": state_b})
    print(f"   判决结果：{result.get('verdict')}")
    print(f"   快速瓶颈距离：{result.get('fast_bottleneck_dist')}")
    print(f"   精确Wasserstein距离：{result.get('dist')}")

    # 场景2：差异拓扑（应该判定分歧）
    print("\n🔹 场景2：差异拓扑（预期：分歧）")
    state_c = {
        "agent_id": "agent-c",
        "h1": [
            {"birth": 0.1, "death": 0.8, "pers": 0.7},
            {"birth": 0.3, "death": 0.9, "pers": 0.6},
            {"birth": 0.5, "death": 1.0, "pers": 0.5}
        ],
        "confidence": 0.85
    }
    state_d = {
        "agent_id": "agent-d",
        "h1": [
            {"birth": 0.05, "death": 0.1, "pers": 0.05}
        ],
        "confidence": 0.9
    }
    result2 = call_mcp_tool("arbitrate", {"state_a": state_c, "state_b": state_d})
    print(f"   判决结果：{result2.get('verdict')}")
    print(f"   弱势Agent：{result2.get('weaker_agent')}")
    print(f"   距离：{result2.get('dist')}")


def test_evolution_flywheel():
    """测试进化飞轮"""
    print("\n" + "=" * 60)
    print("⚙️ 测试5：Reward自进化飞轮")
    print("=" * 60)

    print("\n📤 回传Reward反馈...")
    params = {
        "hole_threshold": 0.1,
        "n_neighbors": 15,
        "min_dist": 0.1,
        "consensus_threshold": 0.5
    }

    # 模拟多轮Reward反馈
    rewards = [2.1, 3.5, 4.2, 3.8, 5.0, 4.7, 3.9, 4.5, 5.2, 4.8]
    for i, r in enumerate(rewards):
        result = call_mcp_tool("send_reward", {
            "agent_id": f"energy-agent-{i+1:02d}",
            "industry": "energy",
            "reward": r,
            "params": params
        })
        print(f"   第{i+1}轮 Reward={r} → 清洗后={result.get('clean_reward')}")

    print("\n✅ Reward反馈完成")
    print("💡 当积累到50条有效反馈后，系统将自动触发贝叶斯优化")
    print("💡 自动迭代出该行业最优TDA超参数")


def main():
    print("\n" + "🚀" * 30)
    print("   Slipknot V4.1 Lite 网关API测试")
    print("🚀" * 30)

    # 生成测试数据
    csv_path = generate_test_data()

    # 1. 健康检查
    if not test_health_check():
        return

    # 2. 工具列表
    test_tools_list()

    # 3. TDA拓扑分析
    data_id = test_tda_analysis(csv_path)

    # 4. 拓扑共识仲裁
    test_consensus_arbitration()

    # 5. 进化飞轮
    test_evolution_flywheel()

    print("\n" + "=" * 60)
    print("🎉 所有网关测试完成！")
    print("=" * 60)
    print("\n📝 审计日志已写入：slipknot_audit.log")
    print("\n💡 下一步：")
    print("   1. 接入你的Agent系统，使用标准MCP协议调用")
    print("   2. 积累业务Reward，让进化飞轮自动优化参数")
    print("   3. 扩展更多行业插件，适配你的业务场景")


if __name__ == "__main__":
    main()
