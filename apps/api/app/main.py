from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routes import auth, dashboard, health, organizations
from app.organization import models as organization_models  # noqa: F401
from app.vendors import models as vendor_models  # noqa: F401
from app.procurement import models as procurement_models  # noqa: F401
from app.organization.routes import router as organization_router
from app.vendors.routes import router as vendors_router
from app.procurement.routes import router as procurement_router
from app.operations import OperationRecord, ProofRecord, router as operations_router, special_router as operations_special_router  # noqa: F401
from app import models  # noqa: F401 - register SQLAlchemy models with metadata

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_env == "development":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TrustFlow 360 API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
app.include_router(organization_router)
app.include_router(vendors_router)
app.include_router(procurement_router)
app.include_router(operations_special_router, prefix="/operations")
app.include_router(operations_router, prefix="/operations")
