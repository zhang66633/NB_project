"""FastAPI application entry point."""

import os
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# 显式加载 .env（确保任何启动方式都能读到）
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown events."""
    settings = get_settings()

    # JWT secret 安全校验
    if settings.jwt_secret == "set-in-env-file":
        if not settings.debug:
            raise RuntimeError(
                "jwt_secret 未配置！生产环境必须在 .env 中设置 JWT_SECRET。"
            )
        import secrets as _secrets
        settings.jwt_secret = _secrets.token_urlsafe(32)
        print(
            "[WARNING] JWT_SECRET 未配置，已生成随机临时密钥（重启后 token 失效）。"
            "请在 .env 中设置 JWT_SECRET。",
            flush=True,
        )

    print(f"MathModelAgent backend starting on {settings.host}:{settings.port}")

    yield

    # Clean up Redis publisher
    from .services.redis_pubsub import shutdown_publisher
    shutdown_publisher()
    print("MathModelAgent backend shutting down.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Math Model Agent",
        description="数学建模多智能体辅助系统",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow frontend dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 全局异常处理器：500 错误返回 JSON 含 traceback，便于排查
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb = traceback.format_exc()
        print(f"[UNHANDLED] {request.method} {request.url.path}\n{tb}", flush=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"{type(exc).__name__}: {str(exc)[:300]}",
                "type": type(exc).__name__,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "type": "RequestValidationError"},
        )

    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
