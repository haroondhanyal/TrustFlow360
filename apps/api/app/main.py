from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routes import auth, health, organizations
from app import models  # noqa: F401 - register SQLAlchemy models with metadata

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_env == "development":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TrustFlow 360 API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])
app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
