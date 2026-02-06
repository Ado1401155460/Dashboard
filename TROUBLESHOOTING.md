# 🔍 Zeabur 常见错误排查指南

## 📋 检查清单

### 1️⃣ 环境变量配置

在 Zeabur 后端服务中，确保配置了以下环境变量：

```env
# ⚠️ 关键：必须使用 postgresql+asyncpg:// 前缀
DATABASE_URL=postgresql+asyncpg://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur

OANDA_API_KEY=dea42dc8b3d6da74c5b582cbc7abc1a4-68c8b88f7b412825b98871fbe495a4a0
OANDA_ACCOUNT_ID=101-003-29767383-002
OANDA_API_URL=https://api-fxpractice.oanda.com
```

### 2️⃣ 常见错误及解决方案

#### 错误 A: "No module named 'asyncpg'"
**原因**: asyncpg 未安装或编译失败

**解决方案**:
- 确保 `requirements.txt` 包含 `asyncpg==0.29.0`
- 确保 `Dockerfile` 安装了 `libpq-dev`
- 使用 Python 3.11（不要用 3.13）

#### 错误 B: "could not connect to server"
**原因**: 数据库连接失败

**解决方案**:
1. 检查 `DATABASE_URL` 格式是否正确
2. 确认使用 `postgresql+asyncpg://` 前缀
3. 检查数据库服务器是否可访问
4. 验证用户名、密码、主机、端口是否正确

#### 错误 C: "No module named 'pydantic_core'"
**原因**: pydantic-core 编译失败

**解决方案**:
- 确保 Dockerfile 安装了 gcc, g++
- 使用 Python 3.11
- 检查是否有足够的内存进行编译

#### 错误 D: "Port already in use"
**原因**: 端口冲突

**解决方案**:
- Zeabur 会自动设置 $PORT
- 确保启动命令使用 `--port ${PORT:-8000}`

#### 错误 E: "Table doesn't exist"
**原因**: 数据库表未创建

**解决方案**:
- 需要先在数据库中创建 `trades` 表
- 或者添加数据库迁移脚本

### 3️⃣ 检查 Dockerfile

确保后端 Dockerfile 包含：

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 4️⃣ 检查 requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
```

### 5️⃣ 数据库表结构

如果数据库中没有 `trades` 表，需要创建：

```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    intent_id TEXT UNIQUE NOT NULL,
    symbol TEXT,
    direction TEXT,
    units DOUBLE PRECISION,
    order_type TEXT,
    entry_price DOUBLE PRECISION,
    current_price DOUBLE PRECISION,
    exit_price DOUBLE PRECISION,
    stop_loss DOUBLE PRECISION,
    take_profit DOUBLE PRECISION,
    status TEXT,
    ai_article TEXT,
    analysisJson JSONB,
    confidence DOUBLE PRECISION,
    oanda_order_id TEXT,
    oanda_trade_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_intent_id ON trades(intent_id);
CREATE INDEX idx_trades_status ON trades(status);
```

## 🔍 如何查看详细错误

### 在 Zeabur 控制台：
1. 进入服务详情页
2. 点击 "Logs" 或"日志"标签
3. 查看最新的错误信息
4. 复制完整的错误堆栈

### 常见日志关键词：
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误
- `Traceback` - Python 错误堆栈
- `Failed to` - 失败信息
- `Connection refused` - 连接被拒绝
- `Module not found` - 模块未找到

## 📝 请提供以下信息

为了更好地帮助您，请提供：

1. **完整的错误日志**（最后 50-100 行）
2. **Zeabur 构建日志**（Build Logs）
3. **Zeabur 运行日志**（Runtime Logs）
4. **环境变量配置截图**（隐藏敏感信息）
5. **具体的错误提示**

## 🚀 快速测试

### 测试数据库连接
```python
# test_db.py
import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(
            'postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur'
        )
        print("✅ 数据库连接成功！")
        await conn.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

asyncio.run(test_connection())
```

### 测试 API
```bash
# 测试健康检查端点
curl https://your-backend.zeabur.app/health

# 测试 API 文档
curl https://your-backend.zeabur.app/docs
```

---

**请将 Zeabur 的错误日志复制粘贴到对话框中，我会帮您详细分析！**

