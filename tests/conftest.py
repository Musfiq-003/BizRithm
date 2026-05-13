# tests/conftest.py
"""Shared pytest fixtures for BizRithm test suite."""
import pytest
import pandas as pd
import numpy as np
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_df():
    """Generate a sample business DataFrame for testing."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="D"),
        "revenue": np.maximum(500, 10000 + np.cumsum(np.random.randn(n) * 300)),
        "quantity": np.random.randint(5, 150, n),
        "product": np.random.choice(["Electronics", "Clothing", "Food"], n),
        "region": np.random.choice(["Dhaka", "Chittagong", "Rajshahi"], n),
        "profit_margin": np.random.uniform(0.1, 0.4, n),
    })


@pytest.fixture
def mock_db():
    """Mock async database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def mock_gemini():
    """Mock Gemini API response."""
    mock = MagicMock()
    mock.generate_content.return_value.text = "Mock AI response for testing."
    return mock
