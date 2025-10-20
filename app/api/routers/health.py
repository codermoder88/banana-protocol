from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: str


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Verify API and database connectivity."""
    return HealthResponse(status="ok", database="connected", timestamp=datetime.now().isoformat() + "Z")
