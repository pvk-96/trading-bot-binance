class TradingBotError(Exception):
    """Base exception for all trading bot errors."""

    pass


class ValidationError(TradingBotError):
    """Raised when input validation fails."""

    pass


class ConfigurationError(TradingBotError):
    """Raised when the bot is misconfigured (e.g., missing credentials)."""

    pass


class APIError(TradingBotError):
    """Raised when the Binance API returns an error."""

    pass
