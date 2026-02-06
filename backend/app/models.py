from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
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
    oanda_order_id = Column(Text)
    oanda_trade_id = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

