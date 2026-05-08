# Test Cases

This document describes the expected behaviour of each feature across all
three interfaces (CLI direct, CLI interactive, GUI).

---

## 1. MARKET BUY order

**Interface**: CLI direct

```bash
python cli.py place-order BTCUSDT BUY MARKET 0.001
```

| Step | Expected |
|------|----------|
| After confirm | Order request table shown with Symbol, Side, Type, Quantity |
| After `y` | Order response table shown with status, orderId, executedQty, avgPrice |
| If filled | Status = `FILLED`, executedQty > 0 |
| If pending | Status = `NEW` or `PARTIALLY_FILLED`, poll attempt made |

**Interface**: GUI

| Step | Expected |
|------|----------|
| Select BTCUSDT, BUY, MARKET | Price field disabled |
| Enter quantity `0.001` | — |
| Click Submit | Button shows "Placing…", then response appears |
| Success | Info popup with order details |

---

## 2. MARKET SELL order

**Interface**: CLI direct

```bash
python cli.py place-order BTCUSDT SELL MARKET 0.001
```

| Step | Expected |
|------|----------|
| Order request | Side = SELL |
| Response | Same as MARKET BUY with SELL side |

---

## 3. LIMIT BUY order

**Interface**: CLI direct

```bash
python cli.py place-order BTCUSDT BUY LIMIT 0.001 --price 76000
```

| Step | Expected |
|------|----------|
| Order request | Includes Price field |
| After confirm | Order placed with type = LIMIT, price = 76000 |

---

## 4. LIMIT SELL order

**Interface**: CLI direct

```bash
python cli.py place-order BTCUSDT SELL LIMIT 0.001 --price 80000
```

| Step | Expected |
|------|----------|
| Order request | Side = SELL, includes Price |
| Response | LIMIT order with GTC timeInForce |

---

## 5. Invalid side

**Input**: `HOLD`

| Interface | Expected behaviour |
|-----------|-------------------|
| CLI direct (with `HOLD`) | `Error: Invalid side 'HOLD'. Must be BUY or SELL.` |
| CLI interactive | Prompt shows only BUY/SELL choices; user cannot enter invalid side |
| GUI | Dropdown restricts to BUY/SELL |

---

## 6. Invalid order type

**Input**: `STOP`

| Interface | Expected behaviour |
|-----------|-------------------|
| CLI direct (with `STOP`) | `Error: Invalid order type 'STOP'. Must be MARKET or LIMIT.` |
| CLI interactive | Prompt shows only MARKET/LIMIT choices |
| GUI | Dropdown restricts to MARKET/LIMIT |

---

## 7. Invalid symbol

**Input**: `NONEXISTENT`

```bash
python cli.py place-order NONEXISTENT BUY MARKET 0.001
```

| Step | Expected |
|------|----------|
| CLI response | Binance API error: "The provided trading pair does not exist on Binance Futures." |
| Log file | Full Binance error logged with code `-1121` |

---

## 8. Negative quantity

**Input**: `-1`

| Interface | Expected behaviour |
|-----------|-------------------|
| CLI direct | Pass `--` before value: `python cli.py place-order BTCUSDT BUY MARKET -- -1`<br>Then: `Error: Quantity must be greater than 0, got -1.0.` |
| CLI interactive | "Quantity must be > 0." and re-prompts |
| GUI | Same validation error via `messagebox` |

> **CLI note**: Tokens starting with `-` are parsed as options by Click/Typer.
> Use `--` to pass negative values. Interactive and GUI modes handle this
> natively.

---

## 9. Zero quantity

**Input**: `0`

| Interface | Expected behaviour |
|-----------|-------------------|
| CLI direct | `Error: Quantity must be greater than 0, got 0.0.` |
| CLI interactive | "Quantity must be > 0." and re-prompts |
| GUI | Same validation error via `messagebox` |

---

## 10. LIMIT order without price

**Input**: CLI direct, LIMIT, no `--price`

```bash
python cli.py place-order BTCUSDT BUY LIMIT 0.001
```

| Step | Expected |
|------|----------|
| CLI | Validation catches missing price → `Error: Invalid price 'None'. Must be a number.` |

**Interface**: GUI

| Step | Expected |
|------|----------|
| Select LIMIT | Price field enabled |
| Leave price empty | `Error: Price is required for LIMIT orders.` popup |

**Interface**: CLI interactive

| Step | Expected |
|------|----------|
| Select LIMIT | Prompt asks for price |
| Leave empty | Continues asking until valid number entered |

---

## 11. CLI interactive — cancellation flow

**Input**: Start interactive, enter valid data, enter `n` at confirmation

```bash
python cli.py interactive
# Symbol: BTCUSDT
# Side: BUY
# Type: MARKET
# Quantity: 0.001
# Place this order? [y/n]: n
```

| Step | Expected |
|------|----------|
| After `n` | `Cancelled.` printed cleanly |
| No traceback | No Python traceback or error log |
| Exit code | Command exits gracefully |

---

## 12. GUI — price field toggling

| Step | Expected |
|------|----------|
| Start GUI | Order Type = MARKET, Price field is disabled |
| Change to LIMIT | Price field becomes enabled |
| Change back to MARKET | Price field cleared and disabled again |
| Clear button | Resets all fields; Price disabled (MARKET default) |

---

## 13. GUI — response area

| Step | Expected |
|------|----------|
| Submit order | Response area shows order details |
| Submit another | New response appended below separator line |
| Clear | Response area cleared |

---

## 14. CLI — missing credentials

```bash
# Temporarily rename .env so credentials are unavailable
mv .env .env.backup
python cli.py place-order BTCUSDT BUY MARKET 0.001
mv .env.backup .env
```

| Step | Expected |
|------|----------|
| Output | `Error: API credentials not found. Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in .env` |

---

## 15. Logging verification

| Step | Expected |
|------|----------|
| Run any command | `logs/trading_bot.log` created |
| Check content | Contains timestamp, level, message |
| INFO level | Order placement and successful responses |
| ERROR level | API errors and validation failures |
| No secrets | API keys NOT visible in log file |

---

## 16. Invalid price for LIMIT

**Input**: `--price 0`

```bash
python cli.py place-order BTCUSDT BUY LIMIT 0.001 --price 0
```

| Step | Expected |
|------|----------|
| CLI | `Error: Price must be greater than 0, got 0.0.` |

---

## 17. GUI — order type dropdown initial state

| Step | Expected |
|------|----------|
| Launch GUI | `MARKET` selected by default |
| Price field | Disabled (greyed out) |
| Switch to LIMIT | Price field enabled |

---

## 18. Symbol dropdown population

| Step | Expected |
|------|----------|
| Launch GUI (with valid credentials) | Combobox populated with TRADING symbols from exchangeInfo |
| On failure | Falls back to default list: BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, SOLUSDT |
| Selection | User can pick any listed symbol |

---

## 19. CLI gui command

```bash
python cli.py gui
```

| Step | Expected |
|------|----------|
| On system with display | GUI window opens |
| On headless system | Error from tkinter (expected) |

---

## 20. Interactive — valid float for quantity

**Input**: `0.5` for quantity

| Step | Expected |
|------|----------|
| CLI interactive | Accepts `0.5`, shows in summary as `0.5` |
| Proceeds to confirmation | — |

---

## Test coverage summary

| Scenario | CLI direct | CLI interactive | GUI |
|----------|-----------|----------------|-----|
| MARKET BUY | ✓ | ✓ | ✓ |
| MARKET SELL | ✓ | ✓ | ✓ |
| LIMIT BUY | ✓ | ✓ | ✓ |
| LIMIT SELL | ✓ | ✓ | ✓ |
| Invalid side | ✓ | N/A (dropdown) | N/A (dropdown) |
| Invalid type | ✓ | N/A (dropdown) | N/A (dropdown) |
| Invalid symbol | ✓ | ✓ | ✓ |
| Negative qty | ✓ | ✓ | ✓ |
| Zero qty | ✓ | ✓ | ✓ |
| LIMIT no price | ✓ | N/A (forced) | ✓ |
| Cancel | ✓ | ✓ | N/A |
| Missing creds | ✓ | ✓ | ✓ |
| Price toggling | N/A | N/A | ✓ |
| Logs generated | ✓ | ✓ | ✓ |
