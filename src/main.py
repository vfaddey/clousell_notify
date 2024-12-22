from fastapi import FastAPI
from src.api.v1.pricing_plans import router as servers_router
from src.api.v1.providers import router as providers_router
from src.core.config import settings

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/",
    title=settings.APP_NAME
)

app.include_router(servers_router)
app.include_router(providers_router)
