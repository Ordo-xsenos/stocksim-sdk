# stocksim-sdk

Official async Python SDK for StockSimulator.

- Python 3.13+
- Async-first (`asyncio` / `httpx`)
- Typed responses via `dataclasses`
- Zero heavy dependencies

## Installation

```bash
pip install stocksim-sdk
```

## Quick Start

```python
import asyncio
from stocksim import StockSimClient

async def main():
    async with StockSimClient(api_key="your-api-key") as client:
        price = await client.get_price("AAPL")
        print(price.ticker, price.price)

asyncio.run(main())
```

## Usage

### Get price

```python
async with StockSimClient(api_key="your-api-key") as client:
    price = await client.get_price("TSLA")
    # PriceResponse(ticker='TSLA', price=182.5, timestamp='2026-06-16T10:00:00Z')
    print(f"{price.ticker}: ${price.price}")
```

### Get portfolio

```python
async with StockSimClient(api_key="your-api-key") as client:
    portfolio = await client.get_portfolio()
    print(f"Balance: ${portfolio.balance:.2f}")
    for pos in portfolio.positions:
        print(f"  {pos.ticker}  qty={pos.quantity}  avg=${pos.avg_price}")
```

### Place an order

```python
async with StockSimClient(api_key="your-api-key") as client:
    order = await client.place_order(ticker="AAPL", action="buy", quantity=5)
    print(f"Order {order.order_id} — {order.status}")
```

## Error Handling

```python
from stocksim import (
    StockSimClient,
    StockSimAuthError,
    StockSimRateLimitError,
    StockSimValidationError,
    StockSimError,
)

async with StockSimClient(api_key="your-api-key") as client:
    try:
        price = await client.get_price("AAPL")
    except StockSimAuthError:
        print("Invalid or missing API key")
    except StockSimRateLimitError as e:
        retry = e.retry_after
        print(f"Rate limit hit — retry after {retry}s")
    except StockSimValidationError as e:
        for err in e.errors:
            print(f"Validation: {err['msg']} at {err['loc']}")
    except StockSimError as e:
        print(f"API error {e.status_code}: {e}")
```

## Manual session management

If you prefer not to use `async with`, call `close()` explicitly:

```python
client = StockSimClient(api_key="your-api-key")
try:
    price = await client.get_price("AAPL")
finally:
    await client.close()
```

## License

MIT
