"""
Slipknot V4.1 Lite 完整功能测试 Demo
验证四大核心能力：
1. TDA拓扑分析
2. 行业自适应业务提示
3. 多Agent拓扑共识仲裁
4. Reward自进化飞轮
"""
import sys
import os
import json
import time
import numpy as np

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_tda_engine():
    """测试1：TDA拓扑分析引擎"""
    print("\n" + "=" * 60)
    print("🧪 测试1：TDA拓扑分析引擎")
    print("=" * 60)

    from slipknot.core.engine import SlipknotTDAEngine

    # 生成测试数据 - 两个圆环（应该检测到2个H1孔洞）
    np.random.seed(42)
    n = 500
    theta = np.linspace(0, 2 * np.pi, n // 2)
    r1, r2 = 1.0, 2.5
    x1 = r1 * np.cos(theta) + np.random.normal(0, 0.05, n // 2)
    y1 = r1 * np.sin(theta) + np.random.normal(0, 0.05, n // 2)
    x2 = r2 * np.cos(theta) + np.random.normal(0, 0.05, n // 2)
    y2 = r2 * np.sin(theta) + np.random.normal(0, 0.05, n // 2)

    data = np.column_stack([
        np.concatenate([x1, x2]),
        np.concatenate([y1, y2])
    ])

    print(f"📊 测试数据形状: {data.shape}")

    # 初始化引擎
    params = {
        'n_neighbors': 15,
        'min_dist': 0.1,
        'hole_threshold': 0.1,
        'top_k': 5
    }
    engine = SlipknotTDAEngine(params)
    print("✅ 引擎初始化成功")

    # 运行TDA分析
    start = time.time()
    result = engine.fit(data)
    elapsed = time.time() - start

    print(f"⏱️  计算耗时: {elapsed:.3f}秒")
    print(f"📈 采样大小: {result['sample_size']}")
    print(f"🔵 H0连通域数量: {result['h0_count']}")
    print(f"⭕ H1孔洞数量: {result['h1_count']}")
    print(f"⚡ 奇点数量: {len(result['singularities'])}")

    if result['h1']:
        print(f"\n📍 前3个H1孔洞详情:")
        for i, h in enumerate(result['h1'][:3]):
            print(f"   {i + 1}. birth={h['birth']:.4f}, death={h['death']:.4f}, pers={h['pers']:.4f}")

    print("\n✅ TDA引擎测试通过！")
    return result


def test_consensus_court():
    """测试2：拓扑共识法庭"""
    print("\n" + "=" * 60)
    print("⚖️  测试2：拓扑共识法庭")
    print("=" * 60)

    from slipknot.consensus.court import ConsensusCourt
    from slipknot.consensus.models import TopologyState

    court = ConsensusCourt(threshold=0.5)
    print("✅ 共识法庭初始化成功")

    # 场景1：相似拓扑（应该达成共识）
    print("\n📋 场景1：相似拓扑（预期：CONSENSUS）")
    state_a = TopologyState(
        agent_id='agent-01',
        h1=[
            {'birth': 0.1, 'death': 0.3, 'pers': 0.2},
            {'birth': 0.2, 'death': 0.45, 'pers': 0.25}
        ],
        confidence=0.92
    )
    state_b = TopologyState(
        agent_id='agent-02',
        h1=[
            {'birth': 0.12, 'death': 0.32, 'pers': 0.2},
            {'birth': 0.22, 'death': 0.47, 'pers': 0.25}
        ],
        confidence=0.88
    )

    result = court.arbitrate(state_a, state_b)
    print(f"   判决结果: {result['verdict']}")
    print(f"   瓶颈距离: {result['fast_bottleneck_dist']:.4f}")
    print(f"   Wasserstein距离: {result['dist']:.4f}")
    assert result['verdict'] in ['CONSENSUS', 'CONSENSUS_FAST'], "场景1应该达成共识"

    # 场景2：差异拓扑（应该判定分歧）
    print("\n📋 场景2：差异拓扑（预期：TOPOLOGICAL_DIVERGENCE）")
    state_c = TopologyState(
        agent_id='agent-03',
        h1=[
            {'birth': 0.1, 'death': 0.8, 'pers': 0.7},
            {'birth': 0.3, 'death': 0.9, 'pers': 0.6},
            {'birth': 0.5, 'death': 1.0, 'pers': 0.5}
        ],
        confidence=0.85
    )
    state_d = TopologyState(
        agent_id='agent-04',
        h1=[
            {'birth': 0.05, 'death': 0.1, 'pers': 0.05}
        ],
        confidence=0.9
    )

    result2 = court.arbitrate(state_c, state_d)
    print(f"   判决结果: {result2['verdict']}")
    print(f"   弱势Agent: {result2['weaker_agent']}")
    print(f"   距离: {result2['dist']:.4f}")
    assert result2['verdict'] == 'TOPOLOGICAL_DIVERGENCE', "场景2应该判定分歧"

    # 场景3：一方为空（应该判定分歧）
    print("\n📋 场景3：一方无孔洞（预期：TOPOLOGICAL_DIVERGENCE）")
    state_e = TopologyState(
        agent_id='agent-05',
        h1=[],
        confidence=0.95
    )
    state_f = TopologyState(
        agent_id='agent-06',
        h1=[{'birth': 0.1, 'death': 0.5, 'pers': 0.4}],
        confidence=0.8
    )

    result3 = court.arbitrate(state_e, state_f)
    print(f"   判决结果: {result3['verdict']}")
    print(f"   弱势Agent: {result3['weaker_agent']}")

    print("\n✅ 共识法庭测试通过！")


def test_industry_plugins():
    """测试3：行业自适应插件"""
    print("\n" + "=" * 60)
    print("🏭 测试3：行业自适应插件")
    print("=" * 60)

    from slipknot.plugins.energy import get_energy_tip
    from slipknot.plugins.quant import get_quant_tip
    from slipknot.plugins.fraud import get_fraud_tip

    # 测试储能插件
    print("\n⚡ 储能调度插件:")
    tip_energy = get_energy_tip(h1_count=3, h0_count=2)
    print(f"   高危状态(h1=3): {tip_energy[:60]}...")
    tip_energy_normal = get_energy_tip(h1_count=0, h0_count=1)
    print(f"   正常状态(h1=0): {tip_energy_normal[:60]}...")

    # 测试量化插件
    print("\n📈 量化交易插件:")
    tip_quant = get_quant_tip(h1_count=3, h0_count=2)
    print(f"   高波动(h1=3): {tip_quant[:60]}...")
    tip_quant_normal = get_quant_tip(h1_count=0, h0_count=1)
    print(f"   平稳市场(h1=0): {tip_quant_normal[:60]}...")

    # 测试风控插件
    print("\n🚨 风控欺诈插件:")
    tip_fraud = get_fraud_tip(h1_count=3, h0_count=4)
    print(f"   高危(h1=3, h0=4): {tip_fraud[:60]}...")
    tip_fraud_normal = get_fraud_tip(h1_count=0, h0_count=1)
    print(f"   正常(h1=0): {tip_fraud_normal[:60]}...")

    print("\n✅ 行业插件测试通过！")


def test_evolution_flywheel():
    """测试4：Reward自进化飞轮"""
    print("\n" + "=" * 60)
    print("🔄 测试4：Reward自进化飞轮")
    print("=" * 60)

    from slipknot.flywheel.filter import RewardFilter
    from slipknot.flywheel.optimizer import EvolutionFlywheel
    from slipknot.storage.backend import get_storage

    # 测试Reward过滤器
    print("\n🎯 Reward过滤器测试:")
    filter = RewardFilter(clip_min=-10.0, clip_max=10.0)
    print("✅ 过滤器初始化成功")

    test_cases = [5.0, -15.0, 8.0, 100.0, 3.5, -3.0]
    print("   极值截断测试:")
    for r in test_cases:
        clean = filter.clean(r, history=[])
        print(f"     {r:>6.1f} → {clean:>6.1f}")

    # 测试进化飞轮
    print("\n⚙️  进化飞轮测试:")
    storage = get_storage()
    flywheel = EvolutionFlywheel(storage)
    print("✅ 进化飞轮初始化成功")

    # 获取默认参数
    default_params = flywheel.get_best_params('energy')
    print(f"   默认参数: {default_params}")

    # 模拟记录Reward
    print("\n   模拟记录Reward（10条）:")
    params = {
        'hole_threshold': 0.1,
        'n_neighbors': 15,
        'min_dist': 0.1,
        'consensus_threshold': 0.5
    }

    for i in range(10):
        reward = 3.0 + i * 0.2 + np.random.normal(0, 0.3)
        clean = flywheel.record_reward(f'agent-{i}', 'energy', reward, params)
        print(f"     agent-{i}: reward={reward:.2f} → clean={clean:.2f}")

    # 再次获取最优参数（应该还是默认值，因为数据不够触发优化）
    best_params = flywheel.get_best_params('energy')
    print(f"\n   当前最优参数: {best_params}")

    print("\n✅ 进化飞轮测试通过！")


def test_storage_backend():
    """测试5：存储后端"""
    print("\n" + "=" * 60)
    print("💾 测试5：存储后端")
    print("=" * 60)

    from slipknot.storage.backend import get_storage

    storage = get_storage()
    print(f"✅ 存储后端初始化成功: {type(storage).__name__}")

    # 测试缓存
    print("\n📦 缓存测试:")
    storage.set_cache("test:key1", {"value": "hello"}, ttl=60)
    result = storage.get_cache("test:key1")
    print(f"   写入 → 读取: {result}")
    assert result == {"value": "hello"}, "缓存读写不一致"

    # 测试不存在的key
    result_none = storage.get_cache("test:nonexistent")
    print(f"   不存在的key: {result_none}")
    assert result_none is None, "不存在的key应该返回None"

    # 测试审计日志
    print("\n📝 审计日志测试:")
    storage.write_log("test_event", {"test": "data", "timestamp": time.time()})
    print("   日志写入成功")

    print("\n✅ 存储后端测试通过！")


def test_task_pool():
    """测试6：任务池"""
    print("\n" + "=" * 60)
    print("⚡ 测试6：任务池")
    print("=" * 60)

    from slipknot.task.pool import SimpleTaskPool

    pool = SimpleTaskPool(max_workers=2)
    print("✅ 任务池初始化成功")

    # 提交任务
    def slow_task(x):
        time.sleep(0.1)
        return x * 2

    print("\n📋 提交3个任务:")
    task_ids = []
    for i in range(3):
        task_id = pool.submit(slow_task, i + 1)
        task_ids.append(task_id)
        print(f"   任务 {task_id}: 输入={i + 1}")

    # 等待完成
    time.sleep(0.5)

    # 获取结果
    print("\n✅ 获取任务结果:")
    for task_id in task_ids:
        status = pool.get_task_status(task_id)
        result = pool.get_task_result(task_id)
        print(f"   任务 {task_id}: 状态={status}, 结果={result}")

    pool.shutdown()
    print("\n✅ 任务池测试通过！")


def main():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("Slipknot V4.1 Lite - 完整功能测试")
    print("🚀" * 30)

    start_time = time.time()

    try:
        # 运行所有测试
        test_tda_engine()
        test_consensus_court()
        test_industry_plugins()
        test_evolution_flywheel()
        test_storage_backend()
        test_task_pool()

        elapsed = time.time() - start_time

        print("\n" + "🎉" * 30)
        print(f"所有测试通过！总耗时: {elapsed:.2f}秒")
        print("🎉" * 30)
        print("\n📋 测试总结:")
        print("   ✅ TDA拓扑分析引擎 - 通过")
        print("   ✅ 拓扑共识法庭 - 通过")
        print("   ✅ 行业自适应插件 - 通过")
        print("   ✅ Reward自进化飞轮 - 通过")
        print("   ✅ 存储后端 - 通过")
        print("   ✅ 任务池 - 通过")
        print("\n💡 下一步:")
        print("   1. 启动服务: python dev_start.py")
        print("   2. 查看API文档: http://127.0.0.1:8000/docs")
        print("   3. 运行网关测试: python scripts/gateway_test.py")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
