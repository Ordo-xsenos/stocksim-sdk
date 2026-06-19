from __future__ import annotations

import pytest
import respx
from httpx import Response

from stocksim import (
    StockSimAuthError,
    StockSimClient,
    StockSimRateLimitError,
    StockSimValidationError,
)
from stocksim.models import OrderResponse, PortfolioResponse, PriceResponse

BASE = "https://api.stocksim.pro"


@pytest.fixture
def client() -> StockSimClient:
    return StockSimClient(api_key="test-key", base_url=BASE)


@respx.mock
@pytest.mark.asyncio
async def test_get_price_success(client: StockSimClient) -> None:
    respx.get(f"{BASE}/prices/AAPL").mock(
        return_value=Response(200, json={"ticker": "AAPL", "price": 182.5, "timestamp": "2026-06-16T10:00:00Z"})
    )

    result = await client.get_price("AAPL")

    assert isinstance(result, PriceResponse)
    assert result.ticker == "AAPL"
    assert result.price == 182.5
    assert result.timestamp == "2026-06-16T10:00:00Z"


@respx.mock
@pytest.mark.asyncio
async def test_get_portfolio_success(client: StockSimClient) -> None:
    respx.get(f"{BASE}/portfolio").mock(
        return_value=Response(
            200,
            json={
                "balance": 10000.0,
                "positions": [{"ticker": "AAPL", "quantity": 5, "avg_price": 175.0}],
            },
        )
    )

    result = await client.get_portfolio()

    assert isinstance(result, PortfolioResponse)
    assert result.balance == 10000.0
    assert len(result.positions) == 1
    assert result.positions[0].ticker == "AAPL"
    assert result.positions[0].quantity == 5


@respx.mock
@pytest.mark.asyncio
async def test_place_order_success(client: StockSimClient) -> None:
    respx.post(f"{BASE}/orders").mock(
        return_value=Response(
            201,
            json={"order_id": "ord-123", "ticker": "TSLA", "action": "buy", "quantity": 10, "status": "filled"},
        )
    )

    result = await client.place_order("TSLA", "buy", 10)

    assert isinstance(result, OrderResponse)
    assert result.order_id == "ord-123"
    assert result.action == "buy"
    assert result.status == "filled"


@respx.mock
@pytest.mark.asyncio
async def test_auth_error_raises_StockSimAuthError(client: StockSimClient) -> None:
    respx.get(f"{BASE}/portfolio").mock(
        return_value=Response(401, json={"detail": "Invalid API key"})
    )

    with pytest.raises(StockSimAuthError) as exc_info:
        await client.get_portfolio()

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value)


@respx.mock
@pytest.mark.asyncio
async def test_forbidden_raises_StockSimAuthError(client: StockSimClient) -> None:
    respx.get(f"{BASE}/portfolio").mock(
        return_value=Response(403, json={"detail": "Forbidden"})
    )

    with pytest.raises(StockSimAuthError) as exc_info:
        await client.get_portfolio()

    assert exc_info.value.status_code == 403


@respx.mock
@pytest.mark.asyncio
async def test_rate_limit_raises_StockSimRateLimitError(client: StockSimClient) -> None:
    respx.get(f"{BASE}/prices/AAPL").mock(
        return_value=Response(
            429,
            json={"detail": "Rate limit exceeded"},
            headers={"Retry-After": "30"},
        )
    )

    with pytest.raises(StockSimRateLimitError) as exc_info:
        await client.get_price("AAPL")

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 30


@respx.mock
@pytest.mark.asyncio
async def test_validation_error_raises_StockSimValidationError(client: StockSimClient) -> None:
    respx.post(f"{BASE}/orders").mock(
        return_value=Response(
            422,
            json={
                "detail": [
                    {"loc": ["body", "quantity"], "msg": "value is not a valid integer", "type": "type_error.integer"}
                ]
            },
        )
    )

    with pytest.raises(StockSimValidationError) as exc_info:
        await client.place_order("AAPL", "buy", -1)

    assert exc_info.value.status_code == 422
    assert len(exc_info.value.errors) == 1
