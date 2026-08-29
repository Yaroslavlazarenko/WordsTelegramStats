"""FastAPI Web Application backend for WordsTelegramStats.

Provides dashboard metrics, live SSE logging, QR auth, and infographics gallery.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.core.config import settings
from src.telegram.auth import get_auth_state
from src.web.routers.actions import router_actions
from src.web.routers.analytics import router_analytics
from src.web.routers.auth import router_auth
from src.web.routers.system import router_system
from src.web.state import state_manager

DIR_WEB = Path(__file__).resolve().parent
DIR_STATIC = DIR_WEB / "static"


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize Telegram client authentication state on server startup."""
    state_auth = await get_auth_state()
    state_manager.auth_status = state_auth.get("status", "unknown")
    state_manager.user_info = state_auth.get("user")
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI web application instance."""
    app_instance = FastAPI(
        title="WordsTelegramStats UI",
        description="Linguistic analytics and infographics dashboard for Telegram chats",
        version="1.0.0",
        lifespan=lifespan,
    )

    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static assets
    app_instance.mount(
        "/static/infographics",
        StaticFiles(directory=str(settings.dir_infographics)),
        name="infographics",
    )
    app_instance.mount(
        "/static",
        StaticFiles(directory=str(DIR_STATIC)),
        name="static",
    )

    # Register API routers
    app_instance.include_router(router_system)
    app_instance.include_router(router_auth)
    app_instance.include_router(router_analytics)
    app_instance.include_router(router_actions)

    @app_instance.get("/", response_class=HTMLResponse)
    async def serve_index() -> FileResponse:
        """Serve the main web dashboard single-page interface."""
        path_index = DIR_STATIC / "index.html"
        return FileResponse(path_index)

    return app_instance


# Application instance for ASGI servers (Uvicorn / Gunicorn)
app = create_app()
