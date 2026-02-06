# 🔧 数据库驱动说明

## ❓ 为什么不需要 psycopg2-binary？

### 我们的架构是**异步**的

本项目使用 **FastAPI 异步架构**，因此需要**异步数据库驱动**。

## 📊 驱动对比

| 特性 | psycopg2-binary | asyncpg |
|------|----------------|---------|
| 类型 | 同步驱动 | 异步驱动 ✅ |
| 性能 | 较慢 | 更快（3-5倍） |
| 适用场景 | 同步应用 | 异步应用 ✅ |
| SQLAlchemy | `create_engine()` | `create_async_engine()` ✅ |
| 连接字符串 | `postgresql://...` | `postgresql+asyncpg://...` ✅ |

## ✅ 我们的配置

### 1. requirements.txt
```txt
sqlalchemy==2.0.25
asyncpg==0.29.0  # ✅ 异步驱动
```

### 2. database.py
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# ✅ 异步引擎
engine = create_async_engine(
    DATABASE_URL,  # postgresql+asyncpg://...
    echo=True
)
```

### 3. .env 配置
```env
# ✅ 注意前缀是 postgresql+asyncpg://
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
```

### 4. API 路由
```python
# ✅ 所有函数都是异步的
@router.get("/pending")
async def get_pending_orders(db: AsyncSession = Depends(get_db)):
    stmt = select(Trade).where(...)
    result = await db.execute(stmt)  # ✅ await
    return result.scalars().all()
```

## ⚠️ 如果添加 psycopg2-binary 会怎样？

1. **不会被使用** - 因为我们用的是 `asyncpg`
2. **增加镜像大小** - 无用的依赖
3. **可能导致混淆** - 两个驱动同时存在
4. **编译问题** - psycopg2-binary 在某些环境下难以编译

## 🔍 如何验证我们使用的是 asyncpg？

### 检查连接字符串
```bash
# 正确的异步连接字符串
postgresql+asyncpg://user:pass@host:port/database

# 错误的同步连接字符串（需要 psycopg2）
postgresql://user:pass@host:port/database
```

### 检查代码
```python
# ✅ 异步代码特征
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
async def get_data():
    result = await db.execute(stmt)
    
# ❌ 同步代码特征（需要 psycopg2）
from sqlalchemy import create_engine
def get_data():
    result = db.execute(stmt)
```

## 📝 总结

| 问题 | 答案 |
|------|------|
| 需要 psycopg2-binary 吗？ | ❌ 不需要 |
| 需要 asyncpg 吗？ | ✅ 需要 |
| 为什么？ | 我们使用异步架构 |
| 连接字符串格式？ | `postgresql+asyncpg://...` |
| 性能如何？ | asyncpg 比 psycopg2 快 3-5 倍 |

## 🚀 如果 Zeabur 提示缺少驱动

请确保：
1. ✅ `requirements.txt` 中有 `asyncpg==0.29.0`
2. ✅ `DATABASE_URL` 使用 `postgresql+asyncpg://` 前缀
3. ✅ `Dockerfile` 中安装了 `libpq-dev`（asyncpg 编译需要）

## 🔧 Dockerfile 中的关键配置

```dockerfile
# ✅ 安装 PostgreSQL 开发库（asyncpg 需要）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev  # ← 这个很重要！
```

---

**结论**: 我们的项目**不需要** `psycopg2-binary`，因为我们使用的是**异步架构 + asyncpg 驱动**。这是正确的配置！✅

