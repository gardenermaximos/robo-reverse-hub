"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.errors import ApiError, api_error_handler
from app.core.registry import setup_registry
from app.api.routes import health, fusion, plan

settings = get_settings()

app = FastAPI(
    title="RCJ Reverse-Engineering Hub",
    version="0.1.0",
    description="Backend for RoboCupJunior Soccer Reverse-Engineering & Prototyping Hub",
)

# CORS — allow the Vite dev server on :5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
app.add_exception_handler(ApiError, api_error_handler)  # type: ignore[arg-type]

# Routers
app.include_router(health.router, prefix="/api")
app.include_router(fusion.router, prefix="/api")
app.include_router(plan.router, prefix="/api")

# Registry setup
setup_registry(enable_electronics=settings.enable_electronics)
