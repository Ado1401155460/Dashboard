from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Text, index=True, unique=True)
    symbol = Column(Text)
    direction = Column(Text)  # "long" 或 "short"
    units = Column(Float)
    order_type = Column(Text)  # "market", "limit", etc.
    entry_price = Column(Float)
    current_price = Column(Float)
    exit_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    status = Column(Text, index=True)  # "pending", "open", "closed"
    ai_article = Column(Text)  # Markdown 格式的分析报告
    analysisJson = Column(JSONB)  # JSON 格式的分析数据
    confidence = Column(Float)
    oanda_order_id = Column(Text, index=True)
    oanda_trade_id = Column(Text, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 新增字段
    realized_pl = Column(Numeric)  # 已实现盈亏
    financing = Column(Numeric)  # 融资费用
    commission = Column(Numeric)  # 佣金
    close_time = Column(DateTime(timezone=True))  # 平仓时间
    close_reason = Column(Text)  # 平仓原因


class AccountSummary(Base):
    __tablename__ = "account_summary"

    account_id = Column(Text, primary_key=True)
    currency = Column(String)
    balance = Column(Numeric)  # 账户余额
    nav = Column(Numeric)  # 净资产价值
    unrealized_pl = Column(Numeric)  # 未实现盈亏
    pl = Column(Numeric)  # 总盈亏
    resettable_pl = Column(Numeric)  # 可重置盈亏
    margin_used = Column(Numeric)  # 已用保证金
    margin_available = Column(Numeric)  # 可用保证金
    margin_call_percent = Column(Numeric)  # 保证金催缴百分比
    position_value = Column(Numeric)  # 持仓价值
    open_trade_count = Column(Integer)  # 持仓数量
    open_order_count = Column(Integer)  # 挂单数量
    last_transaction_id = Column(Text)  # 最后交易ID
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiConfig(Base):
    """API配置表 - 用于存储交易所API配置"""
    __tablename__ = "api_config"

    id = Column(Integer, primary_key=True, index=True)
    exchange_name = Column(String, nullable=False)  # 交易所名称 (OANDA, Binance, etc.)
    api_url = Column(Text, nullable=False)  # API基础URL
    account_id = Column(Text)  # 账户ID
    api_key = Column(Text)  # API Key
    api_secret = Column(Text)  # API Secret (加密存储)
    access_token = Column(Text)  # Access Token
    is_active = Column(Integer, default=1)  # 是否启用 (1=启用, 0=禁用)
    is_testnet = Column(Integer, default=0)  # 是否测试网 (1=是, 0=否)
    extra_config = Column(JSONB)  # 额外配置 (JSON格式)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
