from __future__ import annotations

from types import TracebackType
from typing import Any
import httpx

from exceptions import _raise_for_status
from models import OrderResponse, PortfolioResponse, PriceResponse

_DEFAULT_BASE_URL = "https://api.stocksim.pro"


class StockSimClient:
    """Async HTTP client for the StockSim Pro API."""

    def __init__(self, api_key: str, base_url: str = _DEFAULT_BASE_URL) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-API-Key": api_key},
            timeout=30.0,
        )

    async def __aenter__(self) -> StockSimClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        await self._http.aclose()

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        response = await self._http.request(method, endpoint, **kwargs)
        _raise_for_status(response)
        return response.json()

    async def get_price(self, ticker: str) -> PriceResponse:
        """Fetch the current price for *ticker*."""
        data = await self._request("GET", f"/prices/{ticker}")
        return PriceResponse.from_dict(data)

    async def get_portfolio(self) -> PortfolioResponse:
        """Fetch the authenticated user's portfolio."""
        data = await self._request("GET", "/portfolio")
        return PortfolioResponse.from_dict(data)

    async def place_order(self, ticker: str, action: str, quantity: int) -> OrderResponse:
        """Place a buy/sell order.

        Args:
            ticker: Stock symbol, e.g. ``"AAPL"``.
            action: ``"buy"`` or ``"sell"``.
            quantity: Number of shares.
        """
        data = await self._request(
            "POST",
            "/orders",
            json={"ticker": ticker, "action": action, "quantity": quantity},
        )
        return OrderResponse.from_dict(data)
