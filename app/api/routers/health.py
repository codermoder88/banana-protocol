from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: str


async def _check_database_health(db_session: AsyncSession) -> tuple[str, str]:
    try:
        await db_session.execute(text("SELECT 1"))
        return "ok", "connected"
    except Exception:
        return "error", "disconnected"


@router.get("", response_model=HealthResponse)
async def health_check(db_session: AsyncSession = Depends(get_db_session)) -> HealthResponse:
    status, database_status = await _check_database_health(db_session)

    return HealthResponse(status=status, database=database_status, timestamp=datetime.now().isoformat() + "Z")
