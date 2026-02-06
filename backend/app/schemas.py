from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal

# ==================== 订单相关 ====================

# 挂单列表响应（轻量级，不包含大文本）
class PendingOrderList(BaseModel):
    id: int
    intent_id: str
    symbol: str
    units: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 头寸列表响应（轻量级）
class PositionList(BaseModel):
    id: int
    intent_id: str
    symbol: str
    direction: str
    units: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: Optional[float] = None
    unrealized_pl: Optional[float] = None  # 计算字段
    margin: Optional[float] = None  # 计算字段
    created_at: datetime
    
    class Config:
        from_attributes = True

# 订单详情响应（完整数据，包含大文本）
class OrderDetail(BaseModel):
    id: int
    intent_id: str
    symbol: str
    direction: str
    units: float
    order_type: str
    entry_price: float
    current_price: Optional[float] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: str
    ai_article: Optional[str] = None  # Markdown 分析报告
    analysisJson: Optional[Any] = None
    confidence: Optional[float] = None
    oanda_order_id: Optional[str] = None
    oanda_trade_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    realized_pl: Optional[Decimal] = None
    financing: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    close_time: Optional[datetime] = None
    close_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

# 历史交易记录
class TradeHistory(BaseModel):
    id: int
    intent_id: str
    symbol: str
    direction: str
    units: float
    entry_price: float
    exit_price: Optional[float] = None
    realized_pl: Optional[Decimal] = None
    financing: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    created_at: datetime
    close_time: Optional[datetime] = None
    close_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==================== 账户相关 ====================

# 账户摘要
class AccountSummaryResponse(BaseModel):
    account_id: str
    currency: str
    balance: Decimal
    nav: Decimal
    unrealized_pl: Decimal
    pl: Decimal
    resettable_pl: Decimal
    margin_used: Decimal
    margin_available: Decimal
    margin_call_percent: Decimal
    position_value: Decimal
    open_trade_count: int
    open_order_count: int
    last_transaction_id: str
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== 分析相关 ====================

# 账户统计响应（从 account_summary 获取）
class AccountStats(BaseModel):
    # 从 account_summary 表获取
    total_balance: float
    total_position_value: float
    unrealized_pl: float
    margin_used: float
    margin_available: float
    open_trade_count: int
    open_order_count: int
    
    # 从 trades 表计算
    win_rate: float
    profit_loss_ratio: float
    long_win_rate: float
    short_win_rate: float
    max_drawdown: float
    profit_factor: float
    consecutive_losses: int
    consecutive_wins: int
    avg_holding_time: float  # 小时

# 收益曲线数据点
class EquityCurvePoint(BaseModel):
    date: datetime
    cumulative_profit: float
    balance: float

# 收益曲线响应
class EquityCurveResponse(BaseModel):
    data: list[EquityCurvePoint]

# ==================== Webhook 相关 ====================

# OANDA Webhook 请求
class OandaWebhookPayload(BaseModel):
    type: str  # TRANSACTION, ORDER_FILL, etc.
    time: str
    accountID: str
    batchID: Optional[str] = None
    requestID: Optional[str] = None
    transaction: Optional[dict] = None
    
    class Config:
        extra = "allow"  # 允许额外字段
