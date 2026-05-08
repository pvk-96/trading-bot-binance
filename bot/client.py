import logging
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from bot.exceptions import APIError

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"

_BINANCE_ERROR_MAP = {
    -1121: "The provided trading pair does not exist on Binance Futures.",
    -2019: "Insufficient testnet margin balance for this order. "
    "Use the testnet faucet to credit your account.",
    -4005: "Entered quantity exceeds Binance Futures maximum allowed quantity.",
    -4024: "The LIMIT price violates Binance Futures price filters. "
    "Price must be within the allowed range for this symbol.",
    -1013: "Order rejected by Binance filters. "
    "Check price, quantity, and precision rules for this symbol.",
    -2014: "API-key format is invalid. Check your .env credentials.",
    -2015: "Invalid API-key, IP address, or permissions for this action.",
}


def _user_friendly_message(api_error: BinanceAPIException) -> str:
    code = api_error.code
    base_msg = _BINANCE_ERROR_MAP.get(code)
    if base_msg:
        logger.debug("Mapped error code %s to user-friendly message", code)
        return base_msg
    return api_error.message


class BinanceFuturesClient:
    """Reusable wrapper around the Binance Futures Testnet client."""

    def __init__(self, api_key: str, api_secret: str):
        try:
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.FUTURES_URL = FUTURES_TESTNET_URL
            logger.info("Binance Futures Testnet client initialized")
        except Exception as e:
            logger.error("Failed to initialize Binance client: %s", e)
            raise APIError(f"Failed to initialize Binance client: {e}")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if order_type == "LIMIT" and price is not None:
            params["price"] = price
            params["timeInForce"] = "GTC"

        logger.info(
            "Placing order: symbol=%s side=%s type=%s quantity=%s price=%s",
            symbol,
            side,
            order_type,
            quantity,
            price or "N/A",
        )

        try:
            response = self.client.futures_create_order(**params)
            logger.info(
                "Order response received: orderId=%s status=%s",
                response.get("orderId"),
                response.get("status"),
            )
            return response
        except BinanceAPIException as e:
            logger.error("Binance API error (code=%s): %s", e.code, e)
            raise APIError(_user_friendly_message(e))
        except BinanceOrderException as e:
            logger.error("Binance order error: %s", e)
            raise APIError(f"Order error: {e}")
        except Exception as e:
            logger.exception("Unexpected error placing order")
            raise APIError(f"Unexpected error placing order: {e}")

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        try:
            return self.client.futures_get_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException as e:
            logger.error("Binance API error (order status): %s", e)
            raise APIError(f"Failed to get order status: {e.message}")
        except Exception as e:
            logger.exception("Unexpected error getting order status")
            raise APIError(f"Unexpected error: {e}")

    def get_exchange_info(self) -> dict:
        try:
            return self.client.futures_exchange_info()
        except BinanceAPIException as e:
            logger.error("Binance API error (exchange info): %s", e)
            raise APIError(f"Failed to get exchange info: {e.message}")
        except Exception as e:
            logger.exception("Unexpected error getting exchange info")
            raise APIError(f"Unexpected error: {e}")

    def get_account_info(self) -> dict:
        try:
            return self.client.futures_account()
        except BinanceAPIException as e:
            logger.error("Binance API error (account): %s", e)
            raise APIError(f"Failed to get account info: {e.message}")
        except Exception as e:
            logger.exception("Unexpected error getting account info")
            raise APIError(f"Unexpected error: {e}")
