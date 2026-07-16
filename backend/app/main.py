"""
backend/app/main.py
FastAPI 应用入口 - 服务生命周期管理、路由注册、全局异常处理
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.middleware import setup_middleware

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化资源，关闭时清理资源"""
    logger.info(f"[启动] {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"[配置] LLM模型: {settings.LLM_MODEL}")
    logger.info(f"[配置] 向量数据库: {settings.VECTORSTORE_TYPE}")
    logger.info(f"[配置] 数据库: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'unknown'}")

    # 启动时初始化数据库连接池
    try:
        from app.core.database import get_engine
        engine = get_engine()
        logger.info("[启动] 数据库连接池已初始化")
    except Exception as e:
        logger.warning(f"[启动] 数据库连接池初始化失败（非致命）: {e}")

    yield

    # 关闭时释放资源
    logger.info("[关闭] 正在释放资源...")
    try:
        from app.core.database import get_engine
        engine = get_engine()
        await engine.dispose()
        logger.info("[关闭] 数据库连接池已释放")
    except Exception:
        pass

    try:
        from app.core.redis_client import close_redis
        await close_redis()
        logger.info("[关闭] Redis连接已释放")
    except Exception:
        pass

    logger.info("[关闭] 服务已停止")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 LLM + Agent + RAG 的智能金融分析平台 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 注册自定义中间件
setup_middleware(app)

# GZip 压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 全局异常处理 =====

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常捕获，避免敏感信息泄露到前端"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[异常] request_id={request_id} path={request.url.path} error={str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误，请稍后重试",
            "request_id": request_id,
        },
    )


# ===== 基础端点 =====

@app.get("/health")
async def health_check():
    """健康检查端点，供 Docker / K8s 探活使用"""
    health_status = {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    # 检查数据库连接
    try:
        from app.core.database import get_engine
        from sqlalchemy import text
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"unavailable: {str(e)}"
        health_status["status"] = "degraded"

    # 检查 Redis 连接
    try:
        from app.core.redis_client import get_redis
        redis = await get_redis()
        await redis.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"unavailable: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.get("/")
async def root():
    """根路径，返回基本服务信息"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ===== 注册 API 路由 =====
from app.api import chat, agent, rag, llmops, data

app.include_router(chat.router, prefix="/api/v1", tags=["对话"])
app.include_router(agent.router, prefix="/api/v1", tags=["Agent编排"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG知识库"])
app.include_router(llmops.router, prefix="/api/v1", tags=["LLMOps监控"])
app.include_router(data.router, prefix="/api/v1", tags=["金融数据"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1,
        log_level="info",
    )
