FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p /data/safe_zone tmp

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV MAX_WORKERS=4

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "slipknot.gateway:app", "--host", "0.0.0.0", "--port", "8000"]
