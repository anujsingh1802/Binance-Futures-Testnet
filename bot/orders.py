from __future__ import annotations

import logging
from typing import Any

from bot.client import BinanceFuturesClient

LOGGER = logging.getLogger(__name__)


def build_order_payload(validated: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "symbol": validated["symbol"],
        "side": validated["side"],
        "type": validated["order_type"],
        "quantity": validated["quantity"],
        "newOrderRespType": "RESULT",
    }
    if validated["order_type"] == "LIMIT":
        payload["timeInForce"] = "GTC"
        payload["price"] = validated["price"]
    return payload


def place_order(client: BinanceFuturesClient, validated: dict[str, Any]) -> dict[str, Any]:
    payload = build_order_payload(validated)
    LOGGER.info("Placing order | payload=%s", payload)
    return client.place_order(payload)
