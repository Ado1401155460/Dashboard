from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
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
                    bid = float(price_data["bids"][0]["price"])
                    ask = float(price_data["asks"][0]["price"])
                    return (bid + ask) / 2
    except Exception as e:
        print(f"获取 OANDA 价格失败: {e}")
    return None


def safe_float(value, default=0.0) -> float:
    """安全转换为 float，NULL 返回默认值"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value, default="") -> str:
    """安全转换为 str，NULL 返回默认值"""
    if value is None:
        return default
    return str(value)


@router.get("/pending", response_model=List[PendingOrderList])
async def get_pending_orders(db: AsyncSession = Depends(get_db)):
    """
    获取挂单列表（未成交的限价单）
    使用 defer 延迟加载 ai_article 字段
    容错处理：NULL 值显示为 0 或空字符串
    支持大小写状态值：pending, PENDING
    """
    try:
        # 查询状态为 pending 的订单（支持大小写）
        stmt = select(Trade).where(
            or_(
                func.lower(Trade.status) == 'pending',
                Trade.status == 'pending',
                Trade.status == 'PENDING'
            )
        ).options(
            defer(Trade.ai_article),
            defer(Trade.analysisJson)
        ).order_by(Trade.created_at.desc())
        
        result = await db.execute(stmt)
        trades = result.scalars().all()
        
        # 获取实时价格并构建响应
        orders = []
        for trade in trades:
            # 容错处理：如果 symbol 为 NULL，跳过该订单
            if not trade.symbol:
                continue
            
            current_price = await get_oanda_price(trade.symbol)
            
            orders.append(PendingOrderList(
                id=trade.id,
                intent_id=safe_str(trade.intent_id, f"manual-{trade.id}"),  # NULL 时生成默认 ID
                symbol=safe_str(trade.symbol, "UNKNOWN"),
                units=safe_float(trade.units, 0.0),
                entry_price=safe_float(trade.entry_price, 0.0),
                stop_loss=safe_float(trade.stop_loss),
                take_profit=safe_float(trade.take_profit),
                current_price=safe_float(current_price or trade.current_price, 0.0),
                created_at=trade.created_at
            ))
        
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取挂单列表失败: {str(e)}")


@router.get("/pending/{intent_id}", response_model=OrderDetail)
async def get_pending_order_detail(intent_id: str, db: AsyncSession = Depends(get_db)):
    """
    获取挂单详情（包含完整数据和 AI 分析报告）
    容错处理：NULL 值显示为 0 或空字符串
    支持大小写状态值
    """
    try:
        stmt = select(Trade).where(
            Trade.intent_id == intent_id,
            or_(
                func.lower(Trade.status) == 'pending',
                Trade.status == 'pending',
                Trade.status == 'PENDING'
            )
        )
        result = await db.execute(stmt)
        trade = result.scalar_one_or_none()
        
        if not trade:
            raise HTTPException(status_code=404, detail="挂单不存在")
        
        # 获取实时价格
        if trade.symbol:
            current_price = await get_oanda_price(trade.symbol)
            if current_price:
                trade.current_price = current_price
        
        # 构建响应，所有 NULL 值使用默认值
        return OrderDetail(
            id=trade.id,
            intent_id=safe_str(trade.intent_id, f"manual-{trade.id}"),
            symbol=safe_str(trade.symbol, "UNKNOWN"),
            direction=safe_str(trade.direction, "long"),
            units=safe_float(trade.units, 0.0),
            order_type=safe_str(trade.order_type, "limit"),
            entry_price=safe_float(trade.entry_price, 0.0),
            current_price=safe_float(trade.current_price, 0.0),
            exit_price=safe_float(trade.exit_price),
            stop_loss=safe_float(trade.stop_loss),
            take_profit=safe_float(trade.take_profit),
            status=safe_str(trade.status, "pending"),
            ai_article=safe_str(trade.ai_article),
            analysisJson=trade.analysisJson,
            confidence=safe_float(trade.confidence),
            oanda_order_id=safe_str(trade.oanda_order_id),
            oanda_trade_id=safe_str(trade.oanda_trade_id),
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            realized_pl=trade.realized_pl,
            financing=trade.financing,
            commission=trade.commission,
            close_time=trade.close_time,
            close_reason=safe_str(trade.close_reason)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取挂单详情失败: {str(e)}")
