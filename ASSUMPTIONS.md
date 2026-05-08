# Assumptions

The following assumptions were made during the development of this project:

## Account & Credentials

1. **Futures account enabled** — The testnet account has Futures trading enabled.
2. **Testnet API credentials valid** — The `BINANCE_TESTNET_API_KEY` and
   `BINANCE_TESTNET_API_SECRET` in `.env` are valid and active.
3. **User has symbol permissions** — The API key has permission to trade on the
   requested symbol pairs.

## Network & Environment

4. **Internet connectivity** — A stable internet connection is available to reach
   the Binance Futures Testnet API at `https://testnet.binancefuture.com`.
5. **Python 3.9+** — The project targets Python 3.9 or newer.

## Symbols & Trading

6. **Supported symbols exist** — The requested trading pairs (e.g. BTCUSDT) are
   listed on Binance Futures and are in `"TRADING"` status.
7. **Quantity precision** — The user is responsible for supplying a quantity
   that respects the exchange's `lot_size` and `min_qty` filters. The bot validates
   `quantity > 0` but does not fetch per-symbol precision rules before placing
   orders.

## API Behaviour

8. **Testnet API matches production** — The Binance Futures Testnet API behaves
   identically to the production Futures API in terms of request/response format.
9. **Order response fields** — The `avgPrice` field may be `"0"` or missing for
   MARKET orders until the order is fully filled.

## Project Scope

10. **No advanced strategies** — This project intentionally does **not** implement
    TWAP, Grid, OCO, or any automated trading strategies. It is a manual order
    placement tool.
11. **Single order execution** — Orders are placed one at a time. There is no
    batch-order or bulk-order functionality.

## Logging

12. **Log directory writable** — The process has write permission to the `logs/`
    directory. If the directory does not exist, it is created automatically at
    startup.
