# 量化交易分析仪表盘 🚀

一个基于 **FastAPI + Next.js** 的现代化量化交易分析系统，用于实时同步和分析 OANDA 交易所的订单数据，并展示 AI 驱动的交易分析报告。

![Dashboard](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat-square&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14.1.0-000000?style=flat-square&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)

---

## ✨ 功能特性

### 📊 三大核心模块

#### 1️⃣ 挂单模块
- 📋 实时显示未成交的限价单
- 💹 同步 OANDA 实时市场价格
- 🔍 查看订单详情和 AI 分析报告
- ⏰ 挂单时间追踪

#### 2️⃣ 头寸模块
- 📈 监控已成交的持仓订单
- 💰 实时计算未实现盈亏
- 🎯 显示止损/止盈价格
- 📊 保证金使用情况

#### 3️⃣ 交易分析模块
- 💵 账户总资金与持仓资金
- 🎯 胜率、盈亏比、利润因子
- 📉 最大回撤、连续盈亏统计
- 📈 收益曲线可视化图表
- ⏱️ 平均持仓时间分析

---

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - 异步 ORM
- **PostgreSQL** - 数据库（通过 asyncpg）
- **httpx** - 异步 HTTP 客户端（调用 OANDA API）
- **Pydantic** - 数据验证

### 前端技术栈
- **Next.js 14** - React 框架（App Router）
- **TypeScript** - 类型安全
- **TailwindCSS** - 现代化样式
- **SWR** - 数据获取和缓存
- **Recharts** - 数据可视化
- **React Markdown** - Markdown 渲染

---

## 📁 项目结构

```
Dashboard/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   │   ├── orders.py   # 挂单接口
│   │   │   ├── positions.py # 头寸接口
│   │   │   └── analytics.py # 分析接口
│   │   ├── database.py     # 数据库连接
│   │   ├── models.py       # SQLAlchemy 模型
│   │   ├── schemas.py      # Pydantic 模型
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── Procfile           # Zeabur 部署配置
│
├── frontend/               # Next.js 前端
│   ├── app/
│   │   ├── orders/        # 挂单页面
│   │   ├── positions/     # 头寸页面
│   │   ├── analytics/     # 分析页面
│   │   ├── layout.tsx     # 根布局
│   │   └── page.tsx       # 首页
│   ├── components/        # React 组件
│   ├── lib/              # 工具函数
│   └── package.json      # Node 依赖
│
├── README.md             # 项目说明
├── DEPLOYMENT.md         # 部署指南
├── install.ps1          # 依赖安装脚本
└── start.ps1            # 快速启动脚本
```

---

## 🚀 快速开始

### 前置要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 数据库
- OANDA 交易账户（模拟或真实）

### 1️⃣ 安装依赖

**Windows PowerShell:**
```powershell
.\install.ps1
```

**手动安装:**
```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2️⃣ 配置环境变量

**后端 (`backend/.env`):**
```env
DATABASE_URL=postgresql+asyncpg://root:password@host:port/database
OANDA_API_KEY=your-oanda-api-key
OANDA_ACCOUNT_ID=your-account-id
OANDA_API_URL=https://api-fxpractice.oanda.com
PORT=8000
```

**前端 (`frontend/.env.local`):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3️⃣ 启动服务

**Windows PowerShell:**
```powershell
.\start.ps1
```

**手动启动:**
```bash
# 后端（终端1）
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端（终端2）
cd frontend
npm run dev
```

### 4️⃣ 访问应用

- 🌐 **前端界面**: http://localhost:3000
- 📚 **API 文档**: http://localhost:8000/docs
- 🔧 **API 接口**: http://localhost:8000

---

## 🎨 界面预览

### 设计特色
- 🌙 **深色主题** - 专业的交易终端风格
- 🎭 **玻璃态效果** - 现代化的毛玻璃设计
- 🌈 **渐变色彩** - 蓝紫色调的视觉体验
- ⚡ **流畅动画** - 优雅的过渡效果
- 📱 **响应式布局** - 完美适配各种屏幕

### 字体选择
- **Outfit** - 主要界面字体（优雅现代）
- **JetBrains Mono** - 代码和数字字体（清晰易读）

---

## 🔌 API 端点

### 挂单模块
```
GET  /api/orders/pending              # 获取挂单列表（轻量级）
GET  /api/orders/pending/{intent_id}  # 获取挂单详情（含 AI 报告）
```

### 头寸模块
```
GET  /api/positions/open              # 获取持仓列表（轻量级）
GET  /api/positions/open/{intent_id}  # 获取持仓详情（含 AI 报告）
```

### 交易分析
```
GET  /api/analytics/stats             # 获取账户统计数据
GET  /api/analytics/equity-curve      # 获取收益曲线数据
```

---

## 🎯 核心特性

### ⚡ 异步架构
- 后端全异步实现（asyncio + asyncpg）
- 高并发处理能力
- 非阻塞 I/O 操作

### 🔄 轻重分离
- 列表接口使用 `defer` 延迟加载大文本字段
- 详情接口才加载完整的 AI 分析报告
- 优化数据传输和渲染性能

### 💾 智能缓存
- SWR 全局状态管理
- 自动后台刷新（挂单 5s，持仓 3s）
- 乐观更新和错误重试

### 🎭 骨架屏
- Next.js Loading UI
- 优雅的加载状态
- 提升用户体验

### 📊 实时数据
- 自动同步 OANDA 市场价格
- 实时计算未实现盈亏
- 动态更新收益曲线

---

## 🌐 Zeabur 部署

### 后端部署
1. 创建新服务，选择 `backend` 目录
2. 配置环境变量（见上文）
3. 启动命令：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 前端部署
1. 创建新服务，选择 `frontend` 目录
2. 配置 `NEXT_PUBLIC_API_URL` 为后端 URL
3. Zeabur 自动检测并部署 Next.js

详细部署指南请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📊 数据库表结构

### trades 表（核心表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 主键 |
| `intent_id` | text | 订单唯一标识（关键字段） |
| `symbol` | text | 交易对（如 EUR_USD） |
| `direction` | text | 方向（long/short） |
| `units` | double | 数量 |
| `order_type` | text | 订单类型（market/limit） |
| `entry_price` | double | 入场价格 |
| `current_price` | double | 当前价格 |
| `exit_price` | double | 出场价格 |
| `stop_loss` | double | 止损价 |
| `take_profit` | double | 止盈价 |
| `status` | text | 状态（pending/open/closed） |
| `ai_article` | text | AI 分析报告（Markdown） |
| `analysisJson` | jsonb | 分析数据（JSON） |
| `confidence` | double | 信心指数 |
| `oanda_order_id` | text | OANDA 订单 ID |
| `oanda_trade_id` | text | OANDA 交易 ID |
| `created_at` | timestamp | 创建时间 |
| `updated_at` | timestamp | 更新时间 |

---

## 🛠️ 开发指南

### 添加新的 API 端点
1. 在 `backend/app/routers/` 创建新路由文件
2. 在 `backend/app/main.py` 注册路由
3. 在 `frontend/lib/api.ts` 添加对应的 API 函数

### 添加新的页面
1. 在 `frontend/app/` 创建新目录
2. 添加 `page.tsx` 和 `loading.tsx`
3. 在 `components/Sidebar.tsx` 添加导航链接

### 自定义样式
- 全局样式：`frontend/app/globals.css`
- Markdown 样式：`frontend/app/markdown.css`
- Tailwind 配置：`frontend/tailwind.config.js`

---

## 📝 注意事项

1. ⚠️ **数据库连接**：确保 PostgreSQL 数据库可访问
2. 🔑 **API 密钥**：OANDA API 密钥需要有效且有权限
3. 🌐 **CORS 配置**：生产环境建议配置具体的域名白名单
4. 💾 **数据备份**：定期备份数据库数据
5. 🔒 **安全性**：不要将 `.env` 文件提交到版本控制

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 📧 联系方式

如有问题或建议，请通过 Issue 联系。

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
