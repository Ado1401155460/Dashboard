# 使用官方 Python 3.11 镜像（避免 3.13 兼容性问题）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（编译所需）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 升级 pip 并安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令（支持 Zeabur 的 $PORT 环境变量）
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

