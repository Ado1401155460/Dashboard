# API设置页面 - 数据库迁移说明

## 新增数据表

需要在 PostgreSQL 数据库中创建 `api_config` 表：

```sql
CREATE TABLE api_config (
    id SERIAL PRIMARY KEY,
    exchange_name VARCHAR NOT NULL,
    api_url TEXT NOT NULL,
    account_id TEXT,
    api_key TEXT,
    api_secret TEXT,
    access_token TEXT,
    is_active INTEGER DEFAULT 1,
    is_testnet INTEGER DEFAULT 0,
    extra_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_api_config_is_active ON api_config(is_active);
CREATE INDEX idx_api_config_exchange ON api_config(exchange_name);

-- 插入 OANDA 默认配置（请替换为实际值）
INSERT INTO api_config (
    exchange_name, 
    api_url, 
    account_id, 
    access_token, 
    is_active, 
    is_testnet
) VALUES (
    'OANDA',
    'https://api-fxpractice.oanda.com',
    '你的账户ID',
    '你的Access Token',
    1,
    1
);
```

## 部署步骤

### 1. 更新数据库

在 PostgreSQL 中执行上述 SQL 语句创建表和插入默认配置。

### 2. 部署后端

后端已添加新的路由 `/api/config/`，需要重新部署：

```bash
# 在 Zeabur 后端服务中点击 Redeploy
```

### 3. 部署前端

前端已添加新页面 `/settings`，需要重新部署：

```bash
# 在 Zeabur 前端服务中点击 Redeploy
```

## API 端点

### 获取所有配置
```
GET /api/config/
```

### 获取激活的配置
```
GET /api/config/active
```

### 获取指定配置
```
GET /api/config/{config_id}
```

### 创建配置
```
POST /api/config/
Body: {
  "exchange_name": "OANDA",
  "api_url": "https://api-fxpractice.oanda.com",
  "account_id": "101-001-12345678-001",
  "access_token": "your-token",
  "is_active": 1,
  "is_testnet": 1
}
```

### 更新配置
```
PUT /api/config/{config_id}
Body: { ... }
```

### 删除配置
```
DELETE /api/config/{config_id}
```

### 激活配置
```
POST /api/config/{config_id}/activate
```

## 功能特性

✅ **多交易所支持** - 可以添加多个交易所配置  
✅ **一键切换** - 点击激活按钮即可切换交易所  
✅ **安全存储** - 敏感信息默认隐藏，支持查看  
✅ **测试网支持** - 可标记是否为测试网环境  
✅ **配置管理** - 完整的增删改查功能  

## 注意事项

1. **安全性**：生产环境建议对 `api_secret` 和 `access_token` 进行加密存储
2. **权限控制**：建议添加身份验证，防止未授权访问
3. **配置验证**：建议添加 API 连接测试功能
4. **备份**：修改配置前建议备份原有配置

