from __future__ import annotations

from typing import Any

import httpx


class StockSimError(Exception):
    """Base exception for all StockSim SDK errors."""

    def __init__(self, message: str, *, status_code: int | None = None, detail: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.args[0]!r}, status_code={self.status_code})"


class StockSimAuthError(StockSimError):
    """Raised on 401 Unauthorized or 403 Forbidden responses."""


class StockSimRateLimitError(StockSimError):
    """Raised on 429 Too Many Requests responses."""

    def __init__(self, message: str, *, status_code: int = 429, detail: Any = None, retry_after: int | None = None) -> None:
        super().__init__(message, status_code=status_code, detail=detail)
        self.retry_after = retry_after


class StockSimValidationError(StockSimError):
    """Raised on 422 Unprocessable Entity responses (FastAPI validation errors)."""

    def __init__(self, message: str, *, status_code: int = 422, detail: Any = None) -> None:
        super().__init__(message, status_code=status_code, detail=detail)
        self.errors: list[dict[str, Any]] = detail if isinstance(detail, list) else []


def _raise_for_status(response: httpx.Response) -> None:
    """Parse an error response from the StockSim API and raise the appropriate exception."""
    if response.is_success:
        return

    status_code = response.status_code
    detail: Any = None
    message = f"HTTP {status_code}"

    try:
        body = response.json()
        detail = body.get("detail", body)
        if isinstance(detail, str):
            message = detail
        elif isinstance(detail, list) and detail:
            first = detail[0]
            if isinstance(first, dict):
                message = first.get("msg", message)
    except Exception:
        message = response.text or message

    if status_code in (401, 403):
        raise StockSimAuthError(message, status_code=status_code, detail=detail)
    if status_code == 422:
        raise StockSimValidationError(message, status_code=status_code, detail=detail)
    if status_code == 429:
        retry_after: int | None = None
        raw = response.headers.get("Retry-After")
        if raw is not None:
            try:
                retry_after = int(raw)
            except ValueError:
                pass
        raise StockSimRateLimitError(message, status_code=status_code, detail=detail, retry_after=retry_after)

    raise StockSimError(message, status_code=status_code, detail=detail)
