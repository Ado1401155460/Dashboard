from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import orders, positions, analytics
import os

app = FastAPI(
    title="量化交易分析 API",
    description="用于同步和分析 OANDA 交易所订单数据的 API",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {
        "message": "量化交易分析 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

