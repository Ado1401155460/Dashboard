# 量化交易分析仪表盘 - 部署指南

## Zeabur 部署步骤

### 后端部署

1. 在 Zeabur 创建新项目
2. 添加 Git 仓库或上传代码
3. 选择 `backend` 目录
4. 配置环境变量：
   - `DATABASE_URL`: postgresql+asyncpg://root:EBDYn5xKWIp8V9dH0c21XwQhGR347F6l@hnd1.clusters.zeabur.com:28593/zeabur
   - `OANDA_API_KEY`: dea42dc8b3d6da74c5b582cbc7abc1a4-68c8b88f7b412825b98871fbe495a4a0
   - `OANDA_ACCOUNT_ID`: 101-003-29767383-002
   - `OANDA_API_URL`: https://api-fxpractice.oanda.com
   - `PORT`: 自动设置

5. 启动命令：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 前端部署

1. 在同一项目中添加前端服务
2. 选择 `frontend` 目录
3. 配置环境变量：
   - `NEXT_PUBLIC_API_URL`: 后端服务的 URL（例如：https://your-backend.zeabur.app）

4. Zeabur 会自动检测 Next.js 项目并部署

## 本地开发

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问前端：http://localhost:3000

## API 端点

### 挂单模块
- `GET /api/orders/pending` - 获取挂单列表
- `GET /api/orders/pending/{intent_id}` - 获取挂单详情

### 头寸模块
- `GET /api/positions/open` - 获取持仓列表
- `GET /api/positions/open/{intent_id}` - 获取持仓详情

### 交易分析
- `GET /api/analytics/stats` - 获取账户统计
- `GET /api/analytics/equity-curve` - 获取收益曲线

## 技术特性

✅ **异步架构**：FastAPI + asyncio + asyncpg
✅ **轻重分离**：列表接口延迟加载大文本字段
✅ **实时刷新**：SWR 自动缓存和定时刷新
✅ **骨架屏**：Next.js Loading UI
✅ **响应式设计**：TailwindCSS
✅ **数据可视化**：Recharts
✅ **Markdown 渲染**：React Markdown

## 数据库表结构

主表：`trades`

关键字段：
- `intent_id`: 订单唯一标识
- `status`: pending（挂单）/ open（持仓）/ closed（已平仓）
- `ai_article`: AI 分析报告（Markdown）
- `analysisJson`: 分析数据（JSONB）

## 注意事项

1. 确保 PostgreSQL 数据库可访问
2. OANDA API 密钥需要有效
3. 前端需要配置正确的后端 API URL
4. 生产环境建议配置 CORS 白名单

