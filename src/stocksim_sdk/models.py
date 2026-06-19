from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self


@dataclass(frozen=True)
class PriceResponse:
    ticker: str
    price: float
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            ticker=data["ticker"],
            price=float(data["price"]),
            timestamp=data["timestamp"],
        )


@dataclass(frozen=True)
class PortfolioPosition:
    ticker: str
    quantity: int
    avg_price: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            ticker=data["ticker"],
            quantity=int(data["quantity"]),
            avg_price=float(data["avg_price"]),
        )


@dataclass(frozen=True)
class PortfolioResponse:
    balance: float
    positions: list[PortfolioPosition]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            balance=float(data["balance"]),
            positions=[PortfolioPosition.from_dict(p) for p in data.get("positions", [])],
        )


@dataclass(frozen=True)
class OrderResponse:
    order_id: str
    ticker: str
    action: str
    quantity: int
    status: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            order_id=data["order_id"],
            ticker=data["ticker"],
            action=data["action"],
            quantity=int(data["quantity"]),
            status=data["status"],
        )
