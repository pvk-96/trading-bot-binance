from bot.exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_side(side: str) -> str:
    s = side.upper().strip()
    if s not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.upper().strip()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be MARKET or LIMIT."
        )
    return t


def validate_symbol(symbol: str) -> str:
    s = symbol.upper().strip()
    if not s:
        raise ValidationError("Symbol cannot be empty.")
    if not s.isalnum():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Use only letters and digits."
        )
    return s


def validate_quantity(quantity) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price, order_type: str):
    if order_type != "LIMIT":
        return None
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid price '{price}'. Must be a number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0, got {p}.")
    return p


def validate_order_inputs(symbol, side, order_type, quantity, price=None):
    validated = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }
    if validated["order_type"] == "LIMIT":
        validated["price"] = validate_price(price, "LIMIT")
    return validated
