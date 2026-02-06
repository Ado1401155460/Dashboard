from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Trade, AccountSummary
from app.schemas import AccountStats, EquityCurveResponse, EquityCurvePoint
from typing import List
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", "")

@router.get("/stats", response_model=AccountStats)
async def get_account_stats(db: AsyncSession = Depends(get_db)):
    """
    获取账户统计数据
    - 账户数据从 account_summary 表获取
    - 交易统计从 trades 表计算
    """
    try:
        # 1. 从 account_summary 表获取账户数据
        stmt = select(AccountSummary).where(AccountSummary.account_id == OANDA_ACCOUNT_ID)
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            # 如果没有账户数据，返回默认值
            account_data = {
                "total_balance": 0.0,
                "total_position_value": 0.0,
                "unrealized_pl": 0.0,
                "margin_used": 0.0,
                "margin_available": 0.0,
                "open_trade_count": 0,
                "open_order_count": 0,
            }
        else:
            account_data = {
                "total_balance": float(account.balance),
                "total_position_value": float(account.position_value),
                "unrealized_pl": float(account.unrealized_pl),
                "margin_used": float(account.margin_used),
                "margin_available": float(account.margin_available),
                "open_trade_count": account.open_trade_count,
                "open_order_count": account.open_order_count,
            }
        
        # 2. 从 trades 表计算交易统计
        stmt = select(Trade).where(Trade.status == "closed")
        result = await db.execute(stmt)
        closed_trades = result.scalars().all()
        
        total_trades = len(closed_trades)
        winning_trades = 0
        losing_trades = 0
        total_profit = 0.0
        total_loss = 0.0
        long_wins = 0
        long_total = 0
        short_wins = 0
        short_total = 0
        max_drawdown = 0.0
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        total_holding_time = 0.0
        
        # 计算统计指标
        cumulative_profit = 0.0
        peak_balance = float(account_data["total_balance"])
        
        for trade in closed_trades:
            if trade.realized_pl is not None:
                pl = float(trade.realized_pl)
                
                # 统计方向
                if trade.direction == "long":
                    long_total += 1
                    if pl > 0:
                        long_wins += 1
                else:
                    short_total += 1
                    if pl > 0:
                        short_wins += 1
                
                cumulative_profit += pl
                current_balance = peak_balance + cumulative_profit
                
                # 计算回撤
                if current_balance > peak_balance:
                    peak_balance = current_balance
                drawdown = (peak_balance - current_balance) / peak_balance * 100 if peak_balance > 0 else 0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                
                # 统计盈亏
                if pl > 0:
                    winning_trades += 1
                    total_profit += pl
                    consecutive_wins += 1
                    consecutive_losses = 0
                    if consecutive_wins > max_consecutive_wins:
                        max_consecutive_wins = consecutive_wins
                elif pl < 0:
                    losing_trades += 1
                    total_loss += abs(pl)
                    consecutive_losses += 1
                    consecutive_wins = 0
                    if consecutive_losses > max_consecutive_losses:
                        max_consecutive_losses = consecutive_losses
                
                # 计算持仓时间
                if trade.close_time and trade.created_at:
                    holding_time = (trade.close_time - trade.created_at).total_seconds() / 3600
                    total_holding_time += holding_time
        
        # 计算最终指标
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        long_win_rate = (long_wins / long_total * 100) if long_total > 0 else 0.0
        short_win_rate = (short_wins / short_total * 100) if short_total > 0 else 0.0
        profit_loss_ratio = (total_profit / total_loss) if total_loss > 0 else 0.0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0.0
        avg_holding_time = (total_holding_time / total_trades) if total_trades > 0 else 0.0
        
        return AccountStats(
            # 从 account_summary 获取
            total_balance=round(account_data["total_balance"], 2),
            total_position_value=round(account_data["total_position_value"], 2),
            unrealized_pl=round(account_data["unrealized_pl"], 2),
            margin_used=round(account_data["margin_used"], 2),
            margin_available=round(account_data["margin_available"], 2),
            open_trade_count=account_data["open_trade_count"],
            open_order_count=account_data["open_order_count"],
            # 从 trades 计算
            win_rate=round(win_rate, 2),
            profit_loss_ratio=round(profit_loss_ratio, 2),
            long_win_rate=round(long_win_rate, 2),
            short_win_rate=round(short_win_rate, 2),
            max_drawdown=round(max_drawdown, 2),
            profit_factor=round(profit_factor, 2),
            consecutive_losses=max_consecutive_losses,
            consecutive_wins=max_consecutive_wins,
            avg_holding_time=round(avg_holding_time, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户统计失败: {str(e)}")

@router.get("/equity-curve", response_model=EquityCurveResponse)
async def get_equity_curve(db: AsyncSession = Depends(get_db)):
    """
    获取收益曲线数据（从 trades 表计算，仅统计已平仓订单）
    """
    try:
        # 获取所有已平仓的订单，按时间排序
        stmt = select(Trade).where(Trade.status == "closed").order_by(Trade.close_time)
        result = await db.execute(stmt)
        closed_trades = result.scalars().all()
        
        # 获取初始余额
        stmt = select(AccountSummary).where(AccountSummary.account_id == OANDA_ACCOUNT_ID)
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        initial_balance = float(account.balance) if account else 100000.0
        cumulative_profit = 0.0
        equity_data = []
        
        # 添加起始点
        if closed_trades:
            equity_data.append(EquityCurvePoint(
                date=closed_trades[0].created_at,
                cumulative_profit=0.0,
                balance=initial_balance
            ))
        
        # 计算每笔交易后的累计收益
        for trade in closed_trades:
            if trade.realized_pl is not None:
                pl = float(trade.realized_pl)
                cumulative_profit += pl
                current_balance = initial_balance + cumulative_profit
                
                equity_data.append(EquityCurvePoint(
                    date=trade.close_time or trade.updated_at,
                    cumulative_profit=round(cumulative_profit, 2),
                    balance=round(current_balance, 2)
                ))
        
        return EquityCurveResponse(data=equity_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收益曲线失败: {str(e)}")

@router.get("/history", response_model=List[dict])
async def get_trade_history(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    获取历史交易记录（从 trades 表获取）
    """
    try:
        stmt = select(Trade).where(
            Trade.status == "closed"
        ).order_by(
            Trade.close_time.desc()
        ).limit(limit).offset(offset)
        
        result = await db.execute(stmt)
        trades = result.scalars().all()
        
        history = []
        for trade in trades:
            history.append({
                "id": trade.id,
                "intent_id": trade.intent_id,
                "symbol": trade.symbol,
                "direction": trade.direction,
                "units": trade.units,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "realized_pl": float(trade.realized_pl) if trade.realized_pl else 0.0,
                "financing": float(trade.financing) if trade.financing else 0.0,
                "commission": float(trade.commission) if trade.commission else 0.0,
                "created_at": trade.created_at,
                "close_time": trade.close_time,
                "close_reason": trade.close_reason
            })
        
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")
