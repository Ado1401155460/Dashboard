# 🔍 数据显示问题排查指南

## 问题：挂单模块和头寸模块都没有数据

### 排查步骤（按优先级）

---

## 第一步：检查数据库是否有数据 ⭐ 最重要

### 方法 1：直接访问 API 端点

在浏览器中访问以下 URL：

#### 检查挂单数据
```
https://dashboardbackend.zeabur.app/api/orders/pending
```

**预期结果**：
- ✅ 如果返回 `[]`（空数组）→ 数据库中没有挂单数据
- ✅ 如果返回订单数据 → 后端正常，问题在前端
- ❌ 如果返回错误 → 后端有问题

#### 检查头寸数据
```
https://dashboardbackend.zeabur.app/api/positions/open
```

**预期结果**：
- ✅ 如果返回 `[]`（空数组）→ 数据库中没有持仓数据
- ✅ 如果返回持仓数据 → 后端正常，问题在前端
- ❌ 如果返回错误 → 后端有问题

### 方法 2：查看 API 文档

访问：
```
https://dashboardbackend.zeabur.app/docs
```

在 Swagger 文档中测试 API：
1. 展开 `GET /api/orders/pending`
2. 点击 "Try it out"
3. 点击 "Execute"
4. 查看响应

---

## 第二步：检查数据库表

### 连接数据库

使用 PostgreSQL 客户端连接：
```bash
psql "postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur"
```

### 查询挂单数据
```sql
-- 查看所有挂单
SELECT id, intent_id, symbol, status, created_at 
FROM trades 
WHERE status = 'pending'
ORDER BY created_at DESC;

-- 统计挂单数量
SELECT COUNT(*) FROM trades WHERE status = 'pending';
```

### 查询头寸数据
```sql
-- 查看所有持仓
SELECT id, intent_id, symbol, status, created_at 
FROM trades 
WHERE status = 'open'
ORDER BY created_at DESC;

-- 统计持仓数量
SELECT COUNT(*) FROM trades WHERE status = 'open';
```

### 查看所有订单
```sql
-- 查看所有订单及其状态
SELECT id, intent_id, symbol, status, order_type, created_at 
FROM trades 
ORDER BY created_at DESC 
LIMIT 10;

-- 统计各状态的订单数量
SELECT status, COUNT(*) 
FROM trades 
GROUP BY status;
```

---

## 第三步：检查 OANDA 订单状态

### 在 OANDA 平台查看

1. 登录 OANDA 账户
2. 查看当前挂单和持仓
3. 记录订单 ID

### 对比数据库

检查 OANDA 的订单是否在数据库中：
```sql
-- 根据 OANDA 订单 ID 查询
SELECT * FROM trades WHERE oanda_order_id = '您的订单ID';

-- 根据 OANDA 交易 ID 查询
SELECT * FROM trades WHERE oanda_trade_id = '您的交易ID';
```

---

## 第四步：检查 N8N 工作流

### 验证 N8N 是否在写入数据

1. 进入 N8N 工作流
2. 查看最近的执行记录
3. 检查是否有错误
4. 确认是否写入了 PostgreSQL

### N8N 应该写入的字段

```json
{
  "intent_id": "唯一标识",
  "symbol": "交易对",
  "direction": "long 或 short",
  "units": "数量",
  "order_type": "limit 或 market",
  "entry_price": "价格",
  "stop_loss": "止损",
  "take_profit": "止盈",
  "status": "pending 或 open",
  "oanda_order_id": "OANDA 订单 ID",
  "oanda_trade_id": "OANDA 交易 ID"
}
```

---

## 第五步：检查前端配置

### 验证环境变量

在 Zeabur 前端服务中，检查：
```
NEXT_PUBLIC_API_URL=https://dashboardbackend.zeabur.app
```

**注意**：
- ✅ 必须包含 `https://`
- ✅ 不要在末尾加 `/`
- ✅ 域名必须正确

### 检查浏览器控制台

1. 按 F12 打开开发者工具
2. 切换到 **Console** 标签
3. 查看是否有错误信息

常见错误：
- `Failed to fetch` → API URL 配置错误
- `CORS error` → 跨域问题
- `404 Not Found` → 端点不存在
- `500 Internal Server Error` → 后端错误

### 检查网络请求

1. 按 F12 打开开发者工具
2. 切换到 **Network** 标签
3. 刷新页面
4. 查看 API 请求

检查项：
- 请求 URL 是否正确
- 状态码是什么（200, 404, 500?）
- 响应内容是什么

---

## 第六步：检查后端日志

### 在 Zeabur 查看日志

1. 进入 Zeabur 控制台
2. 选择后端服务
3. 点击 **Logs** 标签
4. 查看最新日志

### 查找关键信息

搜索以下关键词：
- `ERROR` - 错误信息
- `Exception` - 异常
- `Failed` - 失败
- `pending` - 挂单查询
- `open` - 持仓查询

---

## 常见问题及解决方案

### 问题 1：数据库中没有数据

**原因**：N8N 没有写入数据

**解决方案**：
1. 检查 N8N 工作流是否正常运行
2. 确认 N8N 有写入 PostgreSQL 的步骤
3. 检查 N8N 的数据库连接配置
4. 手动运行 N8N 工作流测试

### 问题 2：数据库有数据，但 API 返回空数组

**原因**：状态字段不匹配

**解决方案**：
```sql
-- 检查实际的状态值
SELECT DISTINCT status FROM trades;

-- 可能的状态值：
-- 'PENDING' vs 'pending'
-- 'OPEN' vs 'open'
-- 'FILLED' vs 'open'
```

如果状态值不匹配，更新数据：
```sql
-- 统一状态值为小写
UPDATE trades SET status = LOWER(status);

-- 或者手动修正
UPDATE trades SET status = 'pending' WHERE status = 'PENDING';
UPDATE trades SET status = 'open' WHERE status = 'OPEN' OR status = 'FILLED';
```

### 问题 3：API 返回数据，但前端不显示

**原因**：前端环境变量配置错误

**解决方案**：
1. 检查 `NEXT_PUBLIC_API_URL` 配置
2. 重新部署前端
3. 清除浏览器缓存

### 问题 4：OANDA 有订单，但数据库没有

**原因**：N8N 未同步或 Webhook 未配置

**解决方案**：
1. 手动触发 N8N 工作流同步
2. 配置 OANDA Webhook
3. 手动插入测试数据验证系统

---

## 快速诊断命令

### 一键检查脚本

创建文件 `check_data.sql`：
```sql
-- 检查数据库状态
\echo '=== 数据库连接成功 ==='

\echo '\n=== 挂单统计 ==='
SELECT COUNT(*) as pending_count FROM trades WHERE status = 'pending';

\echo '\n=== 持仓统计 ==='
SELECT COUNT(*) as open_count FROM trades WHERE status = 'open';

\echo '\n=== 所有状态统计 ==='
SELECT status, COUNT(*) as count FROM trades GROUP BY status;

\echo '\n=== 最近10条记录 ==='
SELECT id, intent_id, symbol, status, created_at 
FROM trades 
ORDER BY created_at DESC 
LIMIT 10;

\echo '\n=== 检查 NULL 值 ==='
SELECT 
  COUNT(*) FILTER (WHERE intent_id IS NULL) as null_intent_id,
  COUNT(*) FILTER (WHERE symbol IS NULL) as null_symbol,
  COUNT(*) FILTER (WHERE status IS NULL) as null_status
FROM trades;
```

运行：
```bash
psql "postgresql://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur" -f check_data.sql
```

---

## 测试数据插入

如果数据库为空，可以插入测试数据：

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
```

插入后刷新仪表盘，应该能看到数据。

---

## 诊断流程图

```
开始
  ↓
访问 API 端点
  ↓
有数据？
  ├─ 是 → 前端问题 → 检查环境变量 → 检查浏览器控制台
  └─ 否 → 后端问题
       ↓
     查询数据库
       ↓
     有数据？
       ├─ 是 → 状态字段问题 → 检查 status 值
       └─ 否 → 数据未同步
            ↓
          检查 N8N
            ↓
          N8N 正常？
            ├─ 是 → 检查数据库连接
            └─ 否 → 修复 N8N 工作流
```

---

## 下一步行动

请按照以下顺序排查：

1. ✅ **访问 API 端点**（最快）
   ```
   https://dashboardbackend.zeabur.app/api/orders/pending
   https://dashboardbackend.zeabur.app/api/positions/open
   ```

2. ✅ **查询数据库**（最准确）
   ```sql
   SELECT COUNT(*) FROM trades WHERE status = 'pending';
   SELECT COUNT(*) FROM trades WHERE status = 'open';
   ```

3. ✅ **检查浏览器控制台**（前端问题）
   - 按 F12
   - 查看 Console 和 Network 标签

4. ✅ **查看后端日志**（后端问题）
   - Zeabur 控制台 → 后端服务 → Logs

---

**请先执行第 1 步和第 2 步，然后告诉我结果，我会帮您进一步诊断！** 🔍

