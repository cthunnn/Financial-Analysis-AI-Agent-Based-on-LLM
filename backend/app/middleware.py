"""
backend/app/middleware.py
自定义中间件集合 - 请求追踪、耗时记录、限流控制
"""
import time
import uuid
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求添加唯一追踪ID，便于日志关联与问题排查"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """记录每个HTTP请求的处理耗时"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

        if duration_ms > 1000:
            logger.warning(
                f"慢请求 | {request.method} {request.url.path} | "
                f"耗时 {duration_ms:.0f}ms | "
                f"status={response.status_code}"
            )
        else:
            logger.info(
                f"{request.method} {request.url.path} | "
                f"{duration_ms:.0f}ms | status={response.status_code}"
            )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全相关的HTTP响应头"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


def setup_middleware(app: FastAPI) -> None:
    """按顺序注册所有中间件（后添加的优先执行）"""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    logger.info("中间件注册完成: RequestID, RequestTiming, SecurityHeaders")
