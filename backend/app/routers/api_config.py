from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.database import get_db
from app.models import ApiConfig
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/config", tags=["API配置"])


class ApiConfigCreate(BaseModel):
    exchange_name: str
    api_url: str
    account_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    is_active: int = 1
    is_testnet: int = 0
    extra_config: Optional[Dict[str, Any]] = None


class ApiConfigUpdate(BaseModel):
    exchange_name: Optional[str] = None
    api_url: Optional[str] = None
    account_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    is_active: Optional[int] = None
    is_testnet: Optional[int] = None
    extra_config: Optional[Dict[str, Any]] = None


class ApiConfigResponse(BaseModel):
    id: int
    exchange_name: str
    api_url: str
    account_id: Optional[str]
    api_key: Optional[str]
    api_secret: Optional[str]
    access_token: Optional[str]
    is_active: int
    is_testnet: int
    extra_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ApiConfigResponse])
async def get_all_configs(db: AsyncSession = Depends(get_db)):
    """获取所有API配置"""
    result = await db.execute(select(ApiConfig).order_by(ApiConfig.id))
    configs = result.scalars().all()
    return configs


@router.get("/active", response_model=ApiConfigResponse)
async def get_active_config(db: AsyncSession = Depends(get_db)):
    """获取当前激活的API配置"""
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.is_active == 1).limit(1)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="未找到激活的API配置")
    
    return config


@router.get("/{config_id}", response_model=ApiConfigResponse)
async def get_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """获取指定ID的API配置"""
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return config


@router.post("/", response_model=ApiConfigResponse)
async def create_config(
    config_data: ApiConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新的API配置"""
    
    # 如果新配置设为激活，先禁用其他配置
    if config_data.is_active == 1:
        await db.execute(
            update(ApiConfig).values(is_active=0)
        )
    
    new_config = ApiConfig(**config_data.model_dump())
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    
    return new_config


@router.put("/{config_id}", response_model=ApiConfigResponse)
async def update_config(
    config_id: int,
    config_data: ApiConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新API配置"""
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 如果设为激活，先禁用其他配置
    if config_data.is_active == 1:
        await db.execute(
            update(ApiConfig).where(ApiConfig.id != config_id).values(is_active=0)
        )
    
    # 更新字段
    update_data = config_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)
    
    return config


@router.delete("/{config_id}")
async def delete_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """删除API配置"""
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await db.execute(delete(ApiConfig).where(ApiConfig.id == config_id))
    await db.commit()
    
    return {"message": "配置已删除", "id": config_id}


@router.post("/{config_id}/activate")
async def activate_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """激活指定的API配置"""
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 禁用所有其他配置
    await db.execute(update(ApiConfig).values(is_active=0))
    
    # 激活当前配置
    config.is_active = 1
    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)
    
    return {"message": "配置已激活", "config": config}

