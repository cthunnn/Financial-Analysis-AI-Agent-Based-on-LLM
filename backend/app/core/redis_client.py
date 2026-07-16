"""
backend/app/core/redis_client.py
Redis 连接管理 - 异步 Redis 客户端的延迟初始化与生命周期管理
"""
import redis.asyncio as aioredis
from typing import Optional

from app.config import get_settings

settings = get_settings()
_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """获取或创建 Redis 异步连接（单例）"""
    global _redis
    if _redis is None:
        _redis = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )
    return _redis


async def close_redis() -> None:
    """关闭 Redis 连接"""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
