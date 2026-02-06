from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.database import get_db
from app.models import Trade
from app.schemas import AccountStats, EquityCurveResponse, EquityCurvePoint
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/stats", response_model=AccountStats)
async def get_account_stats(db: AsyncSession = Depends(get_db)):
    """
    获取账户统计数据
    """
    try:
        # 获取所有已平仓的订单用于统计
        stmt = select(Trade).where(Trade.status == "closed")
        result = await db.execute(stmt)
        closed_trades = result.scalars().all()
        
        # 获取所有持仓订单
        stmt_open = select(Trade).where(Trade.status == "open")
        result_open = await db.execute(stmt_open)
        open_trades = result_open.scalars().all()
        
        # 初始化统计变量
        total_balance = 100000.0  # 初始资金，可以从配置读取
        total_position_value = 0.0
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
        
        # 计算已平仓订单的统计
        cumulative_profit = 0.0
        peak_balance = total_balance
        
        for trade in closed_trades:
            if trade.exit_price and trade.entry_price:
                # 计算盈亏
                if trade.direction == "long":
                    pl = (trade.exit_price - trade.entry_price) * trade.units
                    long_total += 1
                    if pl > 0:
                        long_wins += 1
                else:  # short
                    pl = (trade.entry_price - trade.exit_price) * trade.units
                    short_total += 1
                    if pl > 0:
                        short_wins += 1
                
                cumulative_profit += pl
                current_balance = total_balance + cumulative_profit
                
                # 更新峰值和回撤
                if current_balance > peak_balance:
                    peak_balance = current_balance
                drawdown = (peak_balance - current_balance) / peak_balance * 100
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
                if trade.updated_at and trade.created_at:
                    holding_time = (trade.updated_at - trade.created_at).total_seconds() / 3600
                    total_holding_time += holding_time
        
        # 计算持仓总价值
        for trade in open_trades:
            position_value = abs(trade.units * trade.entry_price)
            total_position_value += position_value
        
        # 计算最终统计指标
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        long_win_rate = (long_wins / long_total * 100) if long_total > 0 else 0.0
        short_win_rate = (short_wins / short_total * 100) if short_total > 0 else 0.0
        profit_loss_ratio = (total_profit / total_loss) if total_loss > 0 else 0.0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0.0
        avg_holding_time = (total_holding_time / total_trades) if total_trades > 0 else 0.0
        
        # 更新总资金
        total_balance += cumulative_profit
        
        return AccountStats(
            total_balance=round(total_balance, 2),
            total_position_value=round(total_position_value, 2),
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
    获取收益曲线数据（仅统计已平仓订单）
    """
    try:
        # 获取所有已平仓的订单，按时间排序
        stmt = select(Trade).where(Trade.status == "closed").order_by(Trade.updated_at)
        result = await db.execute(stmt)
        closed_trades = result.scalars().all()
        
        initial_balance = 100000.0  # 初始资金
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
            if trade.exit_price and trade.entry_price:
                # 计算盈亏
                if trade.direction == "long":
                    pl = (trade.exit_price - trade.entry_price) * trade.units
                else:  # short
                    pl = (trade.entry_price - trade.exit_price) * trade.units
                
                cumulative_profit += pl
                current_balance = initial_balance + cumulative_profit
                
                equity_data.append(EquityCurvePoint(
                    date=trade.updated_at or trade.created_at,
                    cumulative_profit=round(cumulative_profit, 2),
                    balance=round(current_balance, 2)
                ))
        
        return EquityCurveResponse(data=equity_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收益曲线失败: {str(e)}")

