# 🛡️ 容错机制说明

## 问题描述

在实际使用中，`trades` 表和 `account_summary` 表的某些字段可能为 NULL：

### 常见 NULL 场景

1. **手动在 OANDA 创建的订单**
   - 没有 `intent_id`（N8N 未生成）
   - 没有 `ai_article`（未生成 AI 分析）
   - 没有 `analysisJson`

2. **部分同步的订单**
   - `realized_pl` 可能为 NULL
   - `financing` 可能为 NULL
   - `commission` 可能为 NULL
   - `close_reason` 可能为 NULL

3. **账户摘要数据**
   - 初次部署时表可能为空
   - 某些字段可能未同步

---

## 解决方案

### 1️⃣ 安全转换函数

在所有路由中添加了三个安全转换函数：

```python
def safe_float(value, default=0.0) -> float:
    """安全转换为 float，NULL 返回默认值"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0) -> int:
    """安全转换为 int，NULL 返回默认值"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_str(value, default="") -> str:
    """安全转换为 str，NULL 返回默认值"""
    if value is None:
        return default
    return str(value)
```

### 2️⃣ 应用场景

#### 场景 A：intent_id 为 NULL
```python
# 手动创建的订单没有 intent_id
intent_id=safe_str(trade.intent_id, f"manual-{trade.id}")
# 结果：NULL → "manual-123"（使用订单 ID 生成）
```

#### 场景 B：realized_pl 为 NULL
```python
# 尝试从 entry_price 和 exit_price 计算
pl = safe_float(trade.realized_pl, 0.0)
if pl == 0.0 and trade.entry_price and trade.exit_price:
    if direction == "long":
        pl = (exit_price - entry_price) * units
    else:
        pl = (entry_price - exit_price) * units
# 结果：NULL → 计算值 或 0.0
```

#### 场景 C：symbol 为 NULL
```python
# 跳过无效订单
if not trade.symbol:
    continue
# 或使用默认值
symbol=safe_str(trade.symbol, "UNKNOWN")
```

#### 场景 D：account_summary 表为空
```python
if not account:
    account_data = {
        "total_balance": 0.0,
        "total_position_value": 0.0,
        # ... 所有字段默认为 0
    }
```

---

## 容错策略

### 📊 数值字段
| 字段类型 | NULL 处理 | 默认值 |
|---------|----------|--------|
| price | `safe_float()` | 0.0 |
| units | `safe_float()` | 0.0 |
| pl | `safe_float()` | 0.0 |
| count | `safe_int()` | 0 |

### 📝 文本字段
| 字段类型 | NULL 处理 | 默认值 |
|---------|----------|--------|
| intent_id | `safe_str()` | `manual-{id}` |
| symbol | `safe_str()` | `UNKNOWN` |
| direction | `safe_str()` | `long` |
| reason | `safe_str()` | `""` |

### 🔢 计算字段
| 字段 | NULL 处理 | 备用计算 |
|------|----------|---------|
| realized_pl | 尝试计算 | `(exit - entry) × units` |
| unrealized_pl | 尝试计算 | `(current - entry) × units` |
| margin | 尝试计算 | `units × price / leverage` |

---

## 更新的文件

✅ `backend/app/routers/orders.py`
- 添加 `safe_float()`, `safe_str()` 函数
- 所有字段使用安全转换
- intent_id 为 NULL 时生成 `manual-{id}`

✅ `backend/app/routers/positions.py`
- 添加 `safe_float()`, `safe_str()` 函数
- 计算函数添加容错处理
- 所有字段使用安全转换

✅ `backend/app/routers/analytics.py`
- 添加 `safe_float()`, `safe_int()`, `safe_str()` 函数
- account_summary 为空时返回默认值
- realized_pl 为 NULL 时尝试计算
- 除零错误处理

---

## 测试场景

### 1. 手动创建的订单（无 intent_id）
```
数据库：intent_id = NULL
显示：intent_id = "manual-123"
结果：✅ 正常显示
```

### 2. 未同步的盈亏数据
```
数据库：realized_pl = NULL
计算：(exit_price - entry_price) × units
结果：✅ 显示计算值
```

### 3. 空的 account_summary 表
```
数据库：无记录
返回：所有字段 = 0
结果：✅ 不报错，显示 0
```

### 4. 缺失的价格数据
```
数据库：entry_price = NULL
显示：entry_price = 0.0
结果：✅ 显示 0，不报错
```

---

## 优势

✅ **不会报错**：NULL 值不会导致整个页面崩溃  
✅ **友好显示**：NULL 显示为 0 或默认值  
✅ **智能计算**：尝试从其他字段计算缺失值  
✅ **向后兼容**：支持手动创建的订单  
✅ **数据完整性**：即使部分数据缺失也能正常工作  

---

**版本**: 2.1.0  
**更新**: 添加全面的容错机制  
**状态**: ✅ 已实现

