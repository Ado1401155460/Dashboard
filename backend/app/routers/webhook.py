from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models import Trade, AccountSummary
from app.schemas import OandaWebhookPayload
from typing import Dict, Any
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()

router = APIRouter(prefix="/api/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", "")
OANDA_API_URL = os.getenv("OANDA_API_URL", "https://api-fxpractice.oanda.com")


async def sync_order_from_oanda(order_id: str, db: AsyncSession):
    """从 OANDA 同步单个订单数据到数据库"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {OANDA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 获取订单详情
            response = await client.get(
                f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders/{order_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                order_data = response.json().get("order", {})
                
                # 查找数据库中的订单
                stmt = select(Trade).where(Trade.oanda_order_id == order_id)
                result = await db.execute(stmt)
                trade = result.scalar_one_or_none()
                
                if trade:
                    # 更新订单状态
                    trade.status = order_data.get("state", "").lower()
                    trade.current_price = float(order_data.get("price", 0))
                    trade.updated_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"订单 {order_id} 已更新")
                else:
                    logger.warning(f"数据库中未找到订单 {order_id}")
                    
    except Exception as e:
        logger.error(f"同步订单失败: {e}")


async def sync_trade_from_oanda(trade_id: str, db: AsyncSession):
    """从 OANDA 同步单个交易数据到数据库"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {OANDA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 获取交易详情
            response = await client.get(
                f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/trades/{trade_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                trade_data = response.json().get("trade", {})
                
                # 查找数据库中的交易
                stmt = select(Trade).where(Trade.oanda_trade_id == trade_id)
                result = await db.execute(stmt)
                trade = result.scalar_one_or_none()
                
                if trade:
                    # 更新交易数据
                    trade.current_price = float(trade_data.get("price", 0))
                    trade.unrealized_pl = float(trade_data.get("unrealizedPL", 0))
                    trade.financing = float(trade_data.get("financing", 0))
                    trade.status = trade_data.get("state", "").lower()
                    trade.updated_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"交易 {trade_id} 已更新")
                else:
                    logger.warning(f"数据库中未找到交易 {trade_id}")
                    
    except Exception as e:
        logger.error(f"同步交易失败: {e}")


async def sync_account_summary(db: AsyncSession):
    """从 OANDA 同步账户摘要到数据库"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {OANDA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 获取账户摘要
            response = await client.get(
                f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/summary",
                headers=headers
            )
            
            if response.status_code == 200:
                account_data = response.json().get("account", {})
                
                # 更新或插入账户摘要
                stmt = select(AccountSummary).where(AccountSummary.account_id == OANDA_ACCOUNT_ID)
                result = await db.execute(stmt)
                account = result.scalar_one_or_none()
                
                if account:
                    # 更新现有记录
                    account.currency = account_data.get("currency")
                    account.balance = float(account_data.get("balance", 0))
                    account.nav = float(account_data.get("NAV", 0))
                    account.unrealized_pl = float(account_data.get("unrealizedPL", 0))
                    account.pl = float(account_data.get("pl", 0))
                    account.resettable_pl = float(account_data.get("resettablePL", 0))
                    account.margin_used = float(account_data.get("marginUsed", 0))
                    account.margin_available = float(account_data.get("marginAvailable", 0))
                    account.margin_call_percent = float(account_data.get("marginCallPercent", 0))
                    account.position_value = float(account_data.get("positionValue", 0))
                    account.open_trade_count = int(account_data.get("openTradeCount", 0))
                    account.open_order_count = int(account_data.get("openPositionCount", 0))
                    account.last_transaction_id = account_data.get("lastTransactionID", "")
                    account.updated_at = datetime.utcnow()
                else:
                    # 插入新记录
                    account = AccountSummary(
                        account_id=OANDA_ACCOUNT_ID,
                        currency=account_data.get("currency"),
                        balance=float(account_data.get("balance", 0)),
                        nav=float(account_data.get("NAV", 0)),
                        unrealized_pl=float(account_data.get("unrealizedPL", 0)),
                        pl=float(account_data.get("pl", 0)),
                        resettable_pl=float(account_data.get("resettablePL", 0)),
                        margin_used=float(account_data.get("marginUsed", 0)),
                        margin_available=float(account_data.get("marginAvailable", 0)),
                        margin_call_percent=float(account_data.get("marginCallPercent", 0)),
                        position_value=float(account_data.get("positionValue", 0)),
                        open_trade_count=int(account_data.get("openTradeCount", 0)),
                        open_order_count=int(account_data.get("openPositionCount", 0)),
                        last_transaction_id=account_data.get("lastTransactionID", ""),
                        updated_at=datetime.utcnow()
                    )
                    db.add(account)
                
                await db.commit()
                logger.info("账户摘要已更新")
                
    except Exception as e:
        logger.error(f"同步账户摘要失败: {e}")


@router.post("/oanda")
async def oanda_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    OANDA Webhook 端点
    接收 OANDA 推送的订单变动通知，实时同步到数据库
    """
    try:
        # 获取原始请求体
        body = await request.json()
        logger.info(f"收到 OANDA Webhook: {body}")
        
        # 解析事件类型
        event_type = body.get("type", "")
        transaction = body.get("transaction", {})
        
        # 根据事件类型处理
        if event_type == "ORDER_FILL":
            # 订单成交
            order_id = transaction.get("orderID")
            trade_id = transaction.get("tradeOpened", {}).get("tradeID")
            
            if order_id:
                await sync_order_from_oanda(order_id, db)
            if trade_id:
                await sync_trade_from_oanda(trade_id, db)
                
        elif event_type == "ORDER_CANCEL":
            # 订单取消
            order_id = transaction.get("orderID")
            if order_id:
                await sync_order_from_oanda(order_id, db)
                
        elif event_type == "TRADE_CLOSE":
            # 交易平仓
            trade_id = transaction.get("tradeID")
            if trade_id:
                # 更新交易为已平仓
                stmt = select(Trade).where(Trade.oanda_trade_id == trade_id)
                result = await db.execute(stmt)
                trade = result.scalar_one_or_none()
                
                if trade:
                    trade.status = "closed"
                    trade.exit_price = float(transaction.get("price", 0))
                    trade.realized_pl = float(transaction.get("realizedPL", 0))
                    trade.financing = float(transaction.get("financing", 0))
                    trade.commission = float(transaction.get("commission", 0))
                    trade.close_time = datetime.utcnow()
                    trade.close_reason = transaction.get("reason", "")
                    trade.updated_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"交易 {trade_id} 已平仓")
        
        # 每次有变动都同步账户摘要
        await sync_account_summary(db)
        
        return {"status": "success", "message": "Webhook 处理成功"}
        
    except Exception as e:
        logger.error(f"Webhook 处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/account")
async def manual_sync_account(db: AsyncSession = Depends(get_db)):
    """手动触发账户摘要同步"""
    try:
        await sync_account_summary(db)
        return {"status": "success", "message": "账户摘要同步成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")

