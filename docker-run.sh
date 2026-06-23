#!/bin/bash
# Slipknot V4.1 Lite Docker 一键部署脚本
# 使用方法：chmod +x docker-run.sh && ./docker-run.sh

set -e

echo "=========================================="
echo "🐳 Slipknot V4.1 Lite Docker 部署"
echo "=========================================="

# 构建镜像
echo "📦 构建Docker镜像..."
docker build -t slipknot-lite:latest .

# 停止旧容器
if docker ps -a --format '{{.Names}}' | grep -q '^slipknot$'; then
    echo "🛑 停止旧容器..."
    docker stop slipknot 2>/dev/null || true
    docker rm slipknot 2>/dev/null || true
fi

# 启动新容器
echo "🚀 启动容器..."
docker run -d \
    --name slipknot \
    -p 8000:8000 \
    -v $(pwd)/tmp:/data/safe_zone \
    -e MAX_WORKERS=4 \
    --restart unless-stopped \
    slipknot-lite:latest

echo ""
echo "✅ 部署完成！"
echo "🌐 服务地址：http://127.0.0.1:8000"
echo "📡 MCP端点：http://127.0.0.1:8000/mcp"
echo "💊 健康检查：http://127.0.0.1:8000/health"
echo ""
echo "📋 查看日志：docker logs -f slipknot"
