# 🔍 数据库数据检查脚本

## 问题确认

✅ 后端 API 正常运行  
❌ 数据库中没有数据（返回空数组）

---

## 立即执行：检查数据库

### 方法 1：使用 psql 命令行

```bash
# 连接数据库
psql "postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur"

# 执行以下查询
```

### 方法 2：使用 SQL 查询

复制以下 SQL 到数据库客户端执行：

```sql
-- 1. 检查 trades 表是否存在
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = 'trades'
);

-- 2. 查看 trades 表的所有数据
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

-- 3. 统计各状态的订单数量
SELECT status, COUNT(*) as count 
FROM trades 
GROUP BY status;

-- 4. 查看所有订单（不限状态）
SELECT id, intent_id, symbol, status, order_type, created_at 
FROM trades 
ORDER BY created_at DESC;

-- 5. 检查是否有 NULL 状态的订单
SELECT COUNT(*) FROM trades WHERE status IS NULL;

-- 6. 查看所有可能的状态值
SELECT DISTINCT status FROM trades;
```

---

## 可能的情况

### 情况 A：trades 表不存在

**解决方案**：创建表

```sql
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    intent_id TEXT UNIQUE,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    realized_pl NUMERIC,
    financing NUMERIC,
    commission NUMERIC,
    close_time TIMESTAMP WITH TIME ZONE,
    close_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_trades_intent_id ON trades(intent_id);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_oanda_order_id ON trades(oanda_order_id);
CREATE INDEX IF NOT EXISTS idx_trades_oanda_trade_id ON trades(oanda_trade_id);
```

### 情况 B：表存在但完全为空

**原因**：N8N 没有写入数据

**解决方案**：

#### 选项 1：检查 N8N 工作流

1. 进入 N8N 工作流
2. 查看执行历史
3. 检查是否有 PostgreSQL 写入步骤
4. 手动执行一次工作流

#### 选项 2：手动插入测试数据

```sql
-- 插入测试挂单
INSERT INTO trades (
  intent_id, symbol, direction, units, order_type,
  entry_price, stop_loss, take_profit, status,
  created_at, updated_at
) VALUES (
  'test-pending-001',
  'EUR_USD',
  'long',
  1000,
  'limit',
  1.0850,
  1.0800,
  1.0900,
  'pending',
  NOW(),
  NOW()
);

-- 插入测试持仓
INSERT INTO trades (
  intent_id, symbol, direction, units, order_type,
  entry_price, stop_loss, take_profit, status,
  created_at, updated_at
) VALUES (
  'test-open-001',
  'GBP_USD',
  'long',
  500,
  'market',
  1.2650,
  1.2600,
  1.2700,
  'open',
  NOW(),
  NOW()
);

-- 验证插入
SELECT * FROM trades WHERE status IN ('pending', 'open');
```

插入后，刷新仪表盘：
```
https://dashboardfrontend.zeabur.app/orders
https://dashboardfrontend.zeabur.app/positions
```

### 情况 C：表有数据但状态值不匹配

**原因**：status 字段值不是 'pending' 或 'open'

**检查**：
```sql
-- 查看所有状态值
SELECT DISTINCT status FROM trades;
```

**可能的值**：
- `PENDING` (大写) ❌
- `OPEN` (大写) ❌
- `FILLED` ❌
- `pending` (小写) ✅
- `open` (小写) ✅

**修复**：
```sql
-- 统一为小写
UPDATE trades SET status = LOWER(status);

-- 或者手动映射
UPDATE trades SET status = 'pending' WHERE status IN ('PENDING', 'PENDING_ORDER');
UPDATE trades SET status = 'open' WHERE status IN ('OPEN', 'FILLED', 'ACTIVE');
UPDATE trades SET status = 'closed' WHERE status IN ('CLOSED', 'CANCELLED');
```

---

## 从 OANDA 同步数据

如果 OANDA 有订单但数据库没有，需要同步：

### 方法 1：使用 N8N 工作流

1. 进入 N8N
2. 找到同步工作流
3. 手动执行
4. 检查是否写入数据库

### 方法 2：手动从 OANDA 获取并插入

如果您在 OANDA 看到订单 ID 为 `163` 的 BTC/USD 订单：

```sql
INSERT INTO trades (
  intent_id,
  symbol,
  direction,
  units,
  order_type,
  entry_price,
  stop_loss,
  take_profit,
  status,
  oanda_order_id,
  created_at,
  updated_at
) VALUES (
  'manual-oanda-163',
  'BTC_USD',  -- 注意：使用下划线
  'long',
  0.004,
  'limit',
  64000.0,
  64600.0,
  64500.0,
  'pending',
  '163',
  NOW(),
  NOW()
);
```

**注意**：
- OANDA 使用 `BTC/USD`（斜杠）
- 数据库应该使用 `BTC_USD`（下划线）

---

## 快速测试脚本

创建文件 `insert_test_data.sql`：

```sql
-- 清空测试数据（可选）
-- DELETE FROM trades WHERE intent_id LIKE 'test-%';

-- 插入多条测试数据
INSERT INTO trades (intent_id, symbol, direction, units, order_type, entry_price, stop_loss, take_profit, status, created_at, updated_at) VALUES
('test-pending-001', 'EUR_USD', 'long', 1000, 'limit', 1.0850, 1.0800, 1.0900, 'pending', NOW(), NOW()),
('test-pending-002', 'GBP_USD', 'short', 800, 'limit', 1.2700, 1.2750, 1.2650, 'pending', NOW(), NOW()),
('test-pending-003', 'USD_JPY', 'long', 5000, 'limit', 149.50, 149.00, 150.00, 'pending', NOW(), NOW()),
('test-open-001', 'EUR_USD', 'long', 1200, 'market', 1.0820, 1.0770, 1.0870, 'open', NOW(), NOW()),
('test-open-002', 'BTC_USD', 'long', 0.01, 'market', 65000, 64000, 66000, 'open', NOW(), NOW()),
('test-open-003', 'XAU_USD', 'short', 10, 'market', 2050, 2060, 2040, 'open', NOW(), NOW());

-- 验证
SELECT COUNT(*) as pending_count FROM trades WHERE status = 'pending';
SELECT COUNT(*) as open_count FROM trades WHERE status = 'open';
SELECT * FROM trades WHERE status IN ('pending', 'open') ORDER BY created_at DESC;
```

执行：
```bash
psql "postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur" -f insert_test_data.sql
```

---

## 验证数据

插入数据后，立即验证：

### 1. 查询数据库
```sql
SELECT * FROM trades WHERE status = 'pending';
SELECT * FROM trades WHERE status = 'open';
```

### 2. 访问 API
```
https://dashboardbackend.zeabur.app/api/orders/pending
https://dashboardbackend.zeabur.app/api/positions/open
```

### 3. 刷新前端
```
https://dashboardfrontend.zeabur.app/orders
https://dashboardfrontend.zeabur.app/positions
```

---

## 下一步行动

请执行以下操作：

### 🔍 步骤 1：查询数据库（必须）

```sql
-- 查看表是否存在
SELECT COUNT(*) FROM trades;

-- 查看所有数据
SELECT * FROM trades LIMIT 10;

-- 查看状态分布
SELECT status, COUNT(*) FROM trades GROUP BY status;
```

### ✅ 步骤 2：根据结果采取行动

**如果表不存在** → 执行创建表的 SQL  
**如果表为空** → 插入测试数据  
**如果有数据但状态不对** → 更新状态值  

### 📊 步骤 3：验证

插入数据后，再次访问：
```
https://dashboardbackend.zeabur.app/api/orders/pending
```

应该能看到数据了！

---

**请告诉我数据库查询的结果，我会帮您进一步处理！** 🔍

