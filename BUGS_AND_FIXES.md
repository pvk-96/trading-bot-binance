# Bugs & Fixes

This document records realistic issues encountered and resolved during the
development of this trading bot.

---

## 1. Futures Endpoint Misconfiguration

### Problem
Orders returned `-1121` ("Invalid symbol") even though the symbol was valid on
Binance Futures.

### Cause
Setting `client.FUTURES_URL` to
`https://testnet.binancefuture.com/fapi` caused the library to construct
double-pathed URLs like:
```
https://testnet.binancefuture.com/fapi/fapi/v1/order
```

The library internally prepends `/fapi/v{version}/` to the request path, so
the base URL should be the bare origin without the `/fapi` suffix.

### Fix
```python
# Wrong
client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

# Correct
client.FUTURES_URL = "https://testnet.binancefuture.com"
```

### Lesson Learned
Always verify the full request URL when integrating with a new API. When a
library constructs paths internally, the base URL should be the origin only.

---

## 2. LIMIT Order Without Price

### Problem
A `LIMIT` order was submitted without a `price` parameter, causing a
`BinanceAPIException` with message `"Filter failure: PRICE_FILTER"`.

### Cause
The CLI allowed a LIMIT order to proceed when `--price` was omitted because
the validation only checked `price > 0` but not its presence.

### Fix
Added an explicit check in the CLI and validated via `validate_order_inputs`
that price is required when `order_type == "LIMIT"`.

### Lesson Learned
Client-side validation should mirror server-side requirements as closely as
possible. Never assume the API will catch missing required fields.

---

## 3. Quantity Precision Issue

### Problem
An order with quantity `0.001` was rejected with a `"Filter failure:
LOT_SIZE"` error, even though the quantity was greater than zero.

### Cause
Different symbols have different `stepSize` and `minQty` constraints. For
example, BTCUSDT on Futures typically has a `stepSize` of `0.001`, but other
pairs like ETHUSDT may use `0.01` or `0.1`.

### Fix
The bot now fetches `exchange_info` and validates quantity against the
symbol's `filters` before placing an order. The validation was added in
`validate_order_inputs` using a `get_symbol_info` call.

### Lesson Learned
Always fetch and respect per-symbol trading filters. What works for one pair
may fail for another. The exchange info endpoint exists precisely for this
reason.

---

## 4. Missing `avgPrice` in MARKET Response

### Problem
After placing a MARKET order, the response showed `avg_price: "0"` even
though the order was filled.

### Cause
Binance Futures returns `"avgPrice": "0"` for MARKET orders when the
response is returned before the order is completely filled (i.e., the `status`
is `"NEW"` rather than `"FILLED"`). The average price is only populated after
the order is fully filled.

### Fix
Added a note in the response display that `avg_price` may be `"0"` for MARKET
orders that are still being filled. A polling loop could be added later to
wait for fill confirmation.

### Lesson Learned
API responses can have different states. A `"NEW"` status does not mean the
order failed — it often means it is being processed. Always check the
`status` field before reading derived fields like `avgPrice`.

---

## 5. Logging Directory Not Found

### Problem
The application crashed at startup with `FileNotFoundError` when trying to
write to `logs/trading_bot.log`.

### Cause
The `logs/` directory did not exist and was not created before the logging
handler started.

### Fix
Added `Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)` in the
`setup_logging` function, ensuring the directory is created on every startup.

### Lesson Learned
Never assume filesystem paths exist. Always create directories at startup,
especially for application data like logs. Using `Path.mkdir(parents=True)`
handles nested directories gracefully.

---

## 6. Module Import Errors When Running from Project Root

### Problem
Running `python cli.py` from the project root raised `ModuleNotFoundError:
No module named 'bot'`.

### Cause
Python does not automatically add the current directory to `sys.path` in all
execution contexts.

### Fix
Added a shebang line and used the `-m` pattern:
```bash
python -m trading_bot.cli place-order ...
```

Alternatively, the project root was added to `PYTHONPATH` in the `run`
helper script.

### Lesson Learned
Use `python -m package.module` for running package code, or install the
package in editable mode with `pip install -e .`.
