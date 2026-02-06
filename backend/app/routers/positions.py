from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import defer
from app.database import get_db
from app.models import Trade
from app.schemas import PositionList, OrderDetail
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

router = APIRouter(prefix="/api/positions", tags=["positions"])

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", "")
OANDA_API_URL = os.getenv("OANDA_API_URL", "https://api-fxpractice.oanda.com")


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


def calculate_unrealized_pl(entry_price: float, current_price: float, units: float, direction: str) -> float:
    """计算未实现盈亏，容错处理"""
    try:
        entry_price = safe_float(entry_price, 0.0)
        current_price = safe_float(current_price, 0.0)
        units = safe_float(units, 0.0)
        
        if entry_price == 0 or current_price == 0 or units == 0:
            return 0.0
        
        if direction == "long":
            return (current_price - entry_price) * units
        else:  # short
            return (entry_price - current_price) * units
    except Exception:
        return 0.0


def calculate_margin(units: float, current_price: float, leverage: float = 50) -> float:
    """计算保证金，容错处理"""
    try:
        units = safe_float(units, 0.0)
        current_price = safe_float(current_price, 0.0)
        
        if units == 0 or current_price == 0:
            return 0.0
        
        return abs(units * current_price) / leverage
    except Exception:
        return 0.0


@router.get("/open", response_model=List[PositionList])
async def get_open_positions(db: AsyncSession = Depends(get_db)):
    """
    获取持仓列表（已成交的订单）
    使用 defer 延迟加载 ai_article 字段
    容错处理：NULL 值显示为 0 或空字符串
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
            # 容错处理：如果 symbol 为 NULL，跳过该订单
            if not trade.symbol:
                continue
            
            current_price = await get_oanda_price(trade.symbol)
            if not current_price:
                current_price = safe_float(trade.current_price, trade.entry_price)
            
            unrealized_pl = calculate_unrealized_pl(
                trade.entry_price,
                current_price,
                trade.units,
                safe_str(trade.direction, "long")
            )
            
            margin = calculate_margin(trade.units, current_price)
            
            positions.append(PositionList(
                id=trade.id,
                intent_id=safe_str(trade.intent_id, f"manual-{trade.id}"),
                symbol=safe_str(trade.symbol, "UNKNOWN"),
                direction=safe_str(trade.direction, "long"),
                units=safe_float(trade.units, 0.0),
                entry_price=safe_float(trade.entry_price, 0.0),
                stop_loss=safe_float(trade.stop_loss),
                take_profit=safe_float(trade.take_profit),
                current_price=safe_float(current_price, 0.0),
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
    容错处理：NULL 值显示为 0 或空字符串
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
            order_type=safe_str(trade.order_type, "market"),
            entry_price=safe_float(trade.entry_price, 0.0),
            current_price=safe_float(trade.current_price, 0.0),
            exit_price=safe_float(trade.exit_price),
            stop_loss=safe_float(trade.stop_loss),
            take_profit=safe_float(trade.take_profit),
            status=safe_str(trade.status, "open"),
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
        raise HTTPException(status_code=500, detail=f"获取持仓详情失败: {str(e)}")
