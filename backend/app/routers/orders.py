from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import defer
from app.database import get_db
from app.models import Trade
from app.schemas import PendingOrderList, OrderDetail
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

router = APIRouter(prefix="/api/orders", tags=["orders"])

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", "")
OANDA_API_URL = os.getenv("OANDA_API_URL", "https://api-fxpractice.oanda.com")

# 获取 OANDA 当前价格
async def get_oanda_price(symbol: str) -> Optional[float]:
    """从 OANDA 获取实时价格"""
    if not OANDA_API_KEY or not OANDA_ACCOUNT_ID:
        print("警告: OANDA API 配置未设置")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {OANDA_API_KEY}",
                "Content-Type": "application/json"
            }
            response = await client.get(
                f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/pricing",
                headers=headers,
                params={"instruments": symbol}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("prices"):
                    price_data = data["prices"][0]
                    # 使用中间价
                    bid = float(price_data["bids"][0]["price"])
                    ask = float(price_data["asks"][0]["price"])
                    return (bid + ask) / 2
    except Exception as e:
        print(f"获取 OANDA 价格失败: {e}")
    return None

@router.get("/pending", response_model=List[PendingOrderList])
async def get_pending_orders(db: AsyncSession = Depends(get_db)):
    """
    获取挂单列表（未成交的限价单）
    使用 defer 延迟加载 ai_article 字段
    """
    try:
        # 查询状态为 pending 的订单，延迟加载大文本字段
        stmt = select(Trade).where(Trade.status == "pending").options(
            defer(Trade.ai_article),
            defer(Trade.analysisJson)
        ).order_by(Trade.created_at.desc())
        
        result = await db.execute(stmt)
        trades = result.scalars().all()
        
        # 获取实时价格并构建响应
        orders = []
        for trade in trades:
            current_price = await get_oanda_price(trade.symbol)
            orders.append(PendingOrderList(
                id=trade.id,
                intent_id=trade.intent_id,
                symbol=trade.symbol,
                units=trade.units,
                entry_price=trade.entry_price,
                stop_loss=trade.stop_loss,
                take_profit=trade.take_profit,
                current_price=current_price or trade.current_price,
                created_at=trade.created_at
            ))
        
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取挂单列表失败: {str(e)}")

@router.get("/pending/{intent_id}", response_model=OrderDetail)
async def get_pending_order_detail(intent_id: str, db: AsyncSession = Depends(get_db)):
    """
    获取挂单详情（包含完整数据和 AI 分析报告）
    """
    try:
        stmt = select(Trade).where(
            Trade.intent_id == intent_id,
            Trade.status == "pending"
        )
        result = await db.execute(stmt)
        trade = result.scalar_one_or_none()
        
        if not trade:
            raise HTTPException(status_code=404, detail="挂单不存在")
        
        # 获取实时价格
        current_price = await get_oanda_price(trade.symbol)
        if current_price:
            trade.current_price = current_price
        
        return OrderDetail.model_validate(trade)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取挂单详情失败: {str(e)}")
