"""Application entrypoint for FastAPI + templated UI."""
from __future__ import annotations

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.routes import router as api_router
from .config import Settings, get_settings

app = FastAPI(title="Google Play Reviews Explorer", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    context = {
        "request": request,
        "defaults": {
            "package_name": settings.default_package_name,
            "translation_language": settings.default_translation_language or "",
            "page_size": settings.default_page_size,
            "recent_window": 72,
        },
        "mock_mode": settings.enable_mock_mode,
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/healthz")
async def healthcheck():
    return {"status": "ok"}
