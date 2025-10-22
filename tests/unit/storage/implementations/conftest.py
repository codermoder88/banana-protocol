from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session() -> Mock:
    mock = Mock(spec=AsyncSession)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.execute = AsyncMock()
    mock.scalar = AsyncMock()
    return mock
