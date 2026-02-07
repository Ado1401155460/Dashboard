from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import orders, positions, analytics, webhook, api_config
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="量化交易分析 API",
    description="用于同步和分析 OANDA 交易所订单数据的 API（双层数据同步架构）",
    version="2.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(orders.router)
app.include_router(positions.router)
app.include_router(analytics.router)
app.include_router(webhook.router)
app.include_router(api_config.router)  # 新增 API配置 路由

@app.get("/")
async def root():
    return {
        "message": "量化交易分析 API v2.1",
        "version": "2.1.0",
        "features": [
            "双层数据同步（N8N 轮询 + OANDA Webhook）",
            "实时价格更新",
            "账户摘要同步",
            "历史交易记录",
            "API配置管理（支持多交易所切换）"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.1.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
