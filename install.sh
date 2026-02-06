#!/bin/bash

echo "========================================"
echo "  量化交易分析仪表盘 - 依赖安装"
echo "========================================"

# 安装后端依赖
echo -e "\n[1/2] 正在安装后端依赖..."
cd backend
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ 后端依赖安装成功！"
else
    echo "✗ 后端依赖安装失败！"
    exit 1
fi

# 安装前端依赖
echo -e "\n[2/2] 正在安装前端依赖..."
cd ../frontend
npm install

if [ $? -eq 0 ]; then
    echo "✓ 前端依赖安装成功！"
else
    echo "✗ 前端依赖安装失败！"
    exit 1
fi

echo -e "\n========================================"
echo "  所有依赖安装完成！"
echo "========================================"
echo -e "\n运行 ./start.sh 启动服务"

