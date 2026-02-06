# 🐳 Docker 部署指南

## 问题解决方案

### 原始问题
后端构建失败的原因：
1. ❌ `pydantic-core` 需要 Rust 编译器
2. ❌ `psycopg2-binary` 与 Python 3.13 不兼容
3. ❌ `asyncpg` 需要编译环境

### 解决方案

#### 1️⃣ 移除 psycopg2-binary
- 我们使用的是 **asyncpg**（异步 PostgreSQL 驱动）
- 不需要 `psycopg2-binary`（同步驱动）
- ✅ 已从 requirements.txt 中移除

#### 2️⃣ 使用 Python 3.11
- 避免 Python 3.13 的兼容性问题
- Python 3.11 对所有依赖都有良好支持
- ✅ Dockerfile 中指定 `python:3.11-slim`

#### 3️⃣ 添加编译依赖
- 安装 `gcc`, `g++`, `make`, `libpq-dev`
- 支持编译 `asyncpg` 和 `pydantic-core`
- ✅ 在 Dockerfile 中添加系统依赖

---

## 📦 新增文件

### 1. backend/Dockerfile
- 使用 Python 3.11-slim 基础镜像
- 安装编译工具和 PostgreSQL 开发库
- 支持 Zeabur 的 $PORT 环境变量

### 2. frontend/Dockerfile
- 使用 Node.js 18-alpine 镜像
- 多阶段构建（优化镜像大小）
- 生产环境优化

### 3. zeabur.yaml
- Zeabur 平台配置文件
- 定义服务依赖关系
- 环境变量配置

### 4. docker-compose.yml
- 本地 Docker 测试配置
- 一键启动前后端服务

---

## 🚀 部署方式

### 方式 1: Zeabur 部署（推荐）

#### 后端部署
1. 在 Zeabur 创建新服务
2. 选择 GitHub 仓库
3. 选择 `backend` 目录
4. Zeabur 会自动检测 Dockerfile 并构建
5. 配置环境变量：
   ```
   DATABASE_URL=postgresql+asyncpg://...
   OANDA_API_KEY=your-key
   OANDA_ACCOUNT_ID=your-account
   OANDA_API_URL=https://api-fxpractice.oanda.com
   ```

#### 前端部署
1. 创建新服务
2. 选择 `frontend` 目录
3. 配置环境变量：
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.zeabur.app
   ```

### 方式 2: Docker Compose（本地测试）

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 2. 编辑 .env 文件，填入真实配置

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

### 方式 3: 手动 Docker 构建

#### 构建后端
```bash
cd backend
docker build -t trading-dashboard-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL="..." \
  -e OANDA_API_KEY="..." \
  -e OANDA_ACCOUNT_ID="..." \
  trading-dashboard-backend
```

#### 构建前端
```bash
cd frontend
docker build -t trading-dashboard-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  trading-dashboard-frontend
```

---

## 🔧 依赖优化说明

### 修改前的 requirements.txt
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
psycopg2-binary==2.9.9  ❌ 不需要（我们用 asyncpg）
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
```

### 修改后的 requirements.txt
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0  ✅ 异步 PostgreSQL 驱动
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
```

---

## 📊 构建优化

### 后端 Dockerfile 特点
- ✅ 使用 Python 3.11（稳定且兼容）
- ✅ 安装编译工具（gcc, g++, make）
- ✅ 安装 libpq-dev（PostgreSQL 开发库）
- ✅ 清理 apt 缓存（减小镜像大小）
- ✅ 支持 $PORT 环境变量

### 前端 Dockerfile 特点
- ✅ 多阶段构建（deps → builder → runner）
- ✅ 使用 alpine 镜像（更小）
- ✅ standalone 输出模式
- ✅ 非 root 用户运行
- ✅ 生产环境优化

---

## 🧪 测试构建

### 测试后端构建
```bash
cd backend
docker build -t test-backend .
```

### 测试前端构建
```bash
cd frontend
docker build -t test-frontend .
```

---

## 📝 环境变量清单

### 后端必需环境变量
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
OANDA_API_KEY=your-oanda-api-key
OANDA_ACCOUNT_ID=your-account-id
OANDA_API_URL=https://api-fxpractice.oanda.com
PORT=8000  # Zeabur 会自动设置
```

### 前端必需环境变量
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## ⚠️ 注意事项

1. **Python 版本**: 必须使用 Python 3.11，不要使用 3.13
2. **编译依赖**: Dockerfile 中必须包含 gcc、g++、libpq-dev
3. **asyncpg**: 是异步驱动，不需要 psycopg2
4. **环境变量**: 确保所有必需的环境变量都已配置
5. **网络**: 确保后端可以访问 PostgreSQL 和 OANDA API

---

## 🎯 推送更新到 GitHub

```bash
cd C:\Users\Administrator\Desktop\Dashboard
git add .
git commit -m "fix: 修复后端构建问题，添加 Docker 配置"
git push origin main
```

---

## ✅ 验证清单

- [x] 移除 psycopg2-binary
- [x] 使用 Python 3.11
- [x] 添加编译依赖
- [x] 创建 Dockerfile（前后端）
- [x] 创建 docker-compose.yml
- [x] 创建 zeabur.yaml
- [x] 更新 next.config.js（standalone 模式）

---

现在您可以重新部署到 Zeabur，构建应该会成功！🚀

