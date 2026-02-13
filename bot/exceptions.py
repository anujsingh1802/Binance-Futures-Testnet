class TradingBotError(Exception):
    """Base exception for the trading bot."""


class ValidationError(TradingBotError):
    """Raised when user input is invalid."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an API error."""


class NetworkError(TradingBotError):
    """Raised when a network error occurs while calling Binance."""
