from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

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
    
    class Config:
        from_attributes = True

# 账户统计响应
class AccountStats(BaseModel):
    total_balance: float
    total_position_value: float
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

