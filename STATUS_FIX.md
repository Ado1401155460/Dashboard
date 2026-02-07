# 🔧 状态值大小写问题修复

## 问题原因

数据库中的状态值是**大写**：
```
"status": "PENDING"  ❌
"status": "OPEN"     ❌
```

但后端代码查询的是**小写**：
```python
WHERE status = 'pending'  ❌
WHERE status = 'open'     ❌
```

导致查询不到数据，API 返回空数组 `[]`。

---

## 解决方案（二选一）

### 方案 1：更新数据库（推荐）⭐

在数据库中执行以下 SQL：

```sql
-- 统一所有状态值为小写
UPDATE trades SET status = LOWER(status);

-- 验证更新
SELECT DISTINCT status FROM trades;
-- 应该看到：pending, open, closed, signal
```

**优点**：
- ✅ 一次性解决
- ✅ 数据统一规范
- ✅ 性能更好（不需要函数转换）

**执行后立即生效**，无需重新部署！

### 方案 2：更新后端代码（已完成）✅

我已经更新了后端代码，支持大小写不敏感匹配：

```python
# 新代码：支持 PENDING 和 pending
stmt = select(Trade).where(
    or_(
        func.lower(Trade.status) == 'pending',
        Trade.status == 'pending',
        Trade.status == 'PENDING'
    )
)
```

**需要重新部署后端**才能生效。

---

## 快速修复步骤

### 选项 A：修改数据库（最快）

1. 连接数据库：
```bash
psql "postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur"
```

2. 执行更新：
```sql
UPDATE trades SET status = LOWER(status);
```

3. 验证：
```sql
SELECT status, COUNT(*) FROM trades GROUP BY status;
```

4. 测试 API：
```
https://dashboardbackend.zeabur.app/api/orders/pending
```

应该能看到数据了！

### 选项 B：重新部署后端

1. 进入 Zeabur 控制台
2. 选择后端服务
3. 点击 **Redeploy**
4. 等待部署完成
5. 测试 API

---

## 验证修复

### 1. 测试 API 端点

```bash
# 测试挂单
curl https://dashboardbackend.zeabur.app/api/orders/pending

# 测试持仓
curl https://dashboardbackend.zeabur.app/api/positions/open
```

### 2. 检查返回数据

应该看到类似这样的数据：
```json
[
  {
    "id": 75,
    "intent_id": "54e1b796c65677c696374434486f4348",
    "symbol": "BTCUSDT",
    "units": 0.0,
    "entry_price": 0.0,
    "stop_loss": null,
    "take_profit": null,
    "current_price": 0.0,
    "created_at": "2026-02-06T..."
  }
]
```

### 3. 刷新前端

访问：
```
https://dashboardfrontend.zeabur.app/orders
https://dashboardfrontend.zeabur.app/positions
```

应该能看到数据显示了！

---

## 其他可能的状态值

根据您的数据，可能还有其他状态值：

```sql
-- 查看所有状态值
SELECT DISTINCT status FROM trades;
```

可能的值：
- `PENDING` → 应该是 `pending`
- `OPEN` → 应该是 `open`
- `CLOSED` → 应该是 `closed`
- `SIGNAL` → 应该是 `signal`
- `FILLED` → 应该映射为 `open`
- `CANCELLED` → 应该映射为 `closed`

### 统一映射

如果需要映射不同的状态值：

```sql
-- 统一状态值
UPDATE trades SET status = 
  CASE 
    WHEN UPPER(status) IN ('PENDING', 'PENDING_ORDER') THEN 'pending'
    WHEN UPPER(status) IN ('OPEN', 'FILLED', 'ACTIVE') THEN 'open'
    WHEN UPPER(status) IN ('CLOSED', 'CANCELLED', 'EXPIRED') THEN 'closed'
    WHEN UPPER(status) = 'SIGNAL' THEN 'signal'
    ELSE LOWER(status)
  END;
```

---

## 推荐操作

**立即执行**（最快解决）：

```sql
-- 1. 连接数据库
psql "postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur"

-- 2. 更新状态值
UPDATE trades SET status = LOWER(status);

-- 3. 验证
SELECT status, COUNT(*) FROM trades GROUP BY status;

-- 4. 退出
\q
```

然后刷新浏览器，数据应该就能显示了！

---

**版本**: 2.1.1  
**修复**: 支持大小写不敏感的状态匹配  
**状态**: ✅ 代码已更新并推送

