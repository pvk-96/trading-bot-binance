import logging
import time
from typing import Optional

from bot.validators import validate_order_inputs

logger = logging.getLogger("trading_bot")

_MARKET_POLL_DELAY = 1.0


class OrderManager:
    """High-level order placement with validation and response formatting."""

    def __init__(self, client):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> dict:
        validated = validate_order_inputs(symbol, side, order_type, quantity, price)

        response = self.client.place_order(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated.get("price"),
        )

        formatted = self._format_response(response, validated)

        if validated["order_type"] == "MARKET":
            formatted = self._poll_market_fill(validated, response, formatted)

        return formatted

    def _poll_market_fill(
        self, validated: dict, response: dict, formatted: dict
    ) -> dict:
        order_id = response.get("orderId")
        status = response.get("status", "")
        if status != "NEW":
            return formatted

        logger.info(
            "MARKET order %s is NEW; polling once after %.1fs for fill status",
            order_id,
            _MARKET_POLL_DELAY,
        )
        time.sleep(_MARKET_POLL_DELAY)

        try:
            updated = self.client.get_order_status(
                symbol=validated["symbol"], order_id=order_id
            )
            new_status = updated.get("status", status)
            if new_status != status:
                logger.info(
                    "MARKET order %s status updated: %s -> %s",
                    order_id,
                    status,
                    new_status,
                )
                formatted = self._format_response(updated, validated)
        except Exception as e:
            logger.warning("Market poll for order %s failed: %s", order_id, e)

        return formatted

    @staticmethod
    def _format_response(response: dict, validated: dict) -> dict:
        return {
            "symbol": validated["symbol"],
            "side": validated["side"],
            "type": validated["order_type"],
            "quantity": validated["quantity"],
            "price": validated.get("price"),
            "order_id": response.get("orderId"),
            "client_order_id": response.get("clientOrderId"),
            "status": response.get("status"),
            "executed_qty": response.get("executedQty"),
            "cum_quote": response.get("cumQuote"),
            "avg_price": response.get("avgPrice"),
        }
