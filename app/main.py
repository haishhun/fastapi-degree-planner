from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.courses import router as courses_router
from app.routers.catalog import router as catalog_router
from app.routers.stats import router as stats_router

app = FastAPI(
    title="CS Degree Planner API",
    version="1.0.0",
    description="Backend API for the Hunter College CS Degree Planner",
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"],
)

app.include_router(
    courses_router,
    prefix="/api/v1/courses",
    tags=["Courses"],
)

app.include_router(
    catalog_router,
    prefix="/api/v1/catalog",
    tags=["Catalog"],
)

app.include_router(
    stats_router,
    prefix="/api/v1/stats",
    tags=["Stats"],
)
