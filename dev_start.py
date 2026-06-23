"""
Slipknot V4.1 Lite 本地开发启动脚本
零中间件依赖，纯Python内存模式运行
一键启动：python dev_start.py
"""
import os
import sys

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Slipknot V4.1 Lite - 轻量拓扑仲裁MCP协处理器")
    print("=" * 60)
    print("📦 运行模式：本地开发（内存存储，无需Redis/MySQL）")
    print("🔧 工作线程：4")
    print("🌐 服务地址：http://0.0.0.0:8000")
    print("📡 MCP端点：http://0.0.0.0:8000/mcp")
    print("💊 健康检查：http://0.0.0.0:8000/health")
    print("=" * 60)
    print("💡 测试命令：python scripts/demo_test.py")
    print("=" * 60)

    import uvicorn
    # 使用纯FastAPI版本网关（无需mcp库依赖，零配置启动）
    # 如需使用标准FastMCP版本，请安装mcp库后改为：slipknot.gateway:app
    uvicorn.run(
        "slipknot.gateway_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
