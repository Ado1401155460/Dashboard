from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import defer
from app.database import get_db
from app.models import Trade
from app.schemas import PositionList, OrderDetail
from typing import List
import httpx
import os

router = APIRouter(prefix="/api/positions", tags=["positions"])

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_API_URL = os.getenv("OANDA_API_URL", "https://api-fxpractice.oanda.com")

async def get_oanda_price(symbol: str) -> float:
    """从 OANDA 获取实时价格"""
    try:
        async with httpx.AsyncClient() as client:
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
                    bid = float(price_data["bids"][0]["price"])
                    ask = float(price_data["asks"][0]["price"])
                    return (bid + ask) / 2
    except Exception as e:
        print(f"获取 OANDA 价格失败: {e}")
    return None

def calculate_unrealized_pl(entry_price: float, current_price: float, units: float, direction: str) -> float:
    """计算未实现盈亏"""
    if direction == "long":
        return (current_price - entry_price) * units
    else:  # short
        return (entry_price - current_price) * units

def calculate_margin(units: float, current_price: float, leverage: float = 50) -> float:
    """计算保证金（假设杠杆为50倍）"""
    return abs(units * current_price) / leverage

@router.get("/open", response_model=List[PositionList])
async def get_open_positions(db: AsyncSession = Depends(get_db)):
    """
    获取持仓列表（已成交的订单）
    使用 defer 延迟加载 ai_article 字段
    """
    try:
        # 查询状态为 open 的订单
        stmt = select(Trade).where(Trade.status == "open").options(
            defer(Trade.ai_article),
            defer(Trade.analysisJson)
        ).order_by(Trade.created_at.desc())
        
        result = await db.execute(stmt)
        trades = result.scalars().all()
        
        # 获取实时价格并计算盈亏
        positions = []
        for trade in trades:
            current_price = await get_oanda_price(trade.symbol)
            if not current_price:
                current_price = trade.current_price or trade.entry_price
            
            unrealized_pl = calculate_unrealized_pl(
                trade.entry_price,
                current_price,
                trade.units,
                trade.direction
            )
            
            margin = calculate_margin(trade.units, current_price)
            
            positions.append(PositionList(
                id=trade.id,
                intent_id=trade.intent_id,
                symbol=trade.symbol,
                direction=trade.direction,
                units=trade.units,
                entry_price=trade.entry_price,
                stop_loss=trade.stop_loss,
                take_profit=trade.take_profit,
                current_price=current_price,
                unrealized_pl=unrealized_pl,
                margin=margin,
                created_at=trade.created_at
            ))
        
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓列表失败: {str(e)}")

@router.get("/open/{intent_id}", response_model=OrderDetail)
async def get_position_detail(intent_id: str, db: AsyncSession = Depends(get_db)):
    """
    获取持仓详情（包含完整数据和 AI 分析报告）
    """
    try:
        stmt = select(Trade).where(
            Trade.intent_id == intent_id,
            Trade.status == "open"
        )
        result = await db.execute(stmt)
        trade = result.scalar_one_or_none()
        
        if not trade:
            raise HTTPException(status_code=404, detail="持仓不存在")
        
        # 获取实时价格
        current_price = await get_oanda_price(trade.symbol)
        if current_price:
            trade.current_price = current_price
        
        return OrderDetail.model_validate(trade)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓详情失败: {str(e)}")

