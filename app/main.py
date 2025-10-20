from fastapi import FastAPI

from app.api.routers import health, metrics, sensors

app = FastAPI(
    title="Weather Sensor API",
    description="API for managing weather sensors and their recorded metrics",
    version="1.0.0",
)

app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(health.router, prefix="/health", tags=["health"])
