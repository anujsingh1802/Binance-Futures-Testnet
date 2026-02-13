from __future__ import annotations

from decimal import Decimal, InvalidOperation

from bot.exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValidationError("symbol must not be empty")
    if not normalized.isalnum():
        raise ValidationError("symbol must be alphanumeric, e.g. BTCUSDT")
    return normalized


def validate_side(side: str) -> str:
    normalized = side.strip().upper()
    if normalized not in VALID_SIDES:
        raise ValidationError(f"side must be one of {sorted(VALID_SIDES)}")
    return normalized


def validate_order_type(order_type: str) -> str:
    normalized = order_type.strip().upper()
    if normalized not in VALID_ORDER_TYPES:
        raise ValidationError(f"order type must be one of {sorted(VALID_ORDER_TYPES)}")
    return normalized


def validate_positive_decimal(raw_value: str | float | int, field_name: str) -> str:
    try:
        value = Decimal(str(raw_value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be numeric") from exc

    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")

    return format(value.normalize(), "f")


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float | int,
    price: str | float | int | None,
) -> dict[str, str]:
    normalized_symbol = normalize_symbol(symbol)
    normalized_side = validate_side(side)
    normalized_order_type = validate_order_type(order_type)
    normalized_quantity = validate_positive_decimal(quantity, "quantity")

    normalized_price = None
    if normalized_order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders")
        normalized_price = validate_positive_decimal(price, "price")

    return {
        "symbol": normalized_symbol,
        "side": normalized_side,
        "order_type": normalized_order_type,
        "quantity": normalized_quantity,
        "price": normalized_price,
    }
