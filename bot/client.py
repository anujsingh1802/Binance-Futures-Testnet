from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bot.exceptions import BinanceAPIError, NetworkError

LOGGER = logging.getLogger(__name__)


@dataclass
class BinanceFuturesClient:
    api_key: str
    api_secret: str
    base_url: str = "https://testnet.binancefuture.com"
    timeout: float = 10.0
    mock_mode: bool = False

    def _sign(self, params: dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _headers(self) -> dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key}

    def place_order(self, order_payload: dict[str, Any]) -> dict[str, Any]:
        if self.mock_mode:
            return self._mock_order_response(order_payload)

        endpoint = "/fapi/v1/order"
        url = f"{self.base_url.rstrip('/')}{endpoint}"

        params = dict(order_payload)
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        params["signature"] = self._sign(params)

        safe_payload = dict(params)
        safe_payload.pop("signature", None)
        LOGGER.info("API request | POST %s | payload=%s", endpoint, safe_payload)

        encoded = urlencode(params).encode("utf-8")
        request = Request(url, data=encoded, headers=self._headers(), method="POST")

        try:
            with urlopen(request, timeout=self.timeout) as response:
                status_code = response.getcode()
                response_text = response.read().decode("utf-8")
        except HTTPError as exc:
            response_text = exc.read().decode("utf-8")
            LOGGER.error("API response | status=%s | body=%s", exc.code, response_text)
            try:
                body = json.loads(response_text)
            except json.JSONDecodeError:
                raise BinanceAPIError(f"HTTP {exc.code}: {response_text}") from exc
            message = body.get("msg", response_text)
            code = body.get("code", "unknown")
            raise BinanceAPIError(f"Binance API error (code={code}): {message}") from exc
        except URLError as exc:
            LOGGER.exception("Network error calling Binance")
            raise NetworkError(f"Network error: {exc}") from exc

        LOGGER.info("API response | status=%s | body=%s", status_code, response_text)

        try:
            body = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise BinanceAPIError(f"Invalid JSON response: {response_text}") from exc

        if status_code >= 400:
            message = body.get("msg", response_text)
            code = body.get("code", "unknown")
            raise BinanceAPIError(f"Binance API error (code={code}): {message}")

        return body

    def _mock_order_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        current_time = int(time.time() * 1000)
        order_type = payload["type"]
        mock_response = {
            "clientOrderId": "mock-order-id",
            "cumQty": payload["quantity"],
            "cumQuote": "0",
            "executedQty": payload["quantity"] if order_type == "MARKET" else "0",
            "orderId": int(current_time / 1000),
            "avgPrice": payload.get("price", "0") if order_type == "LIMIT" else "65000.0",
            "origQty": payload["quantity"],
            "price": payload.get("price", "0"),
            "reduceOnly": False,
            "side": payload["side"],
            "positionSide": "BOTH",
            "status": "FILLED" if order_type == "MARKET" else "NEW",
            "symbol": payload["symbol"],
            "timeInForce": payload.get("timeInForce", "GTC"),
            "type": order_type,
            "updateTime": current_time,
            "workingType": "CONTRACT_PRICE",
        }
        LOGGER.info("MOCK API request | payload=%s", payload)
        LOGGER.info("MOCK API response | body=%s", mock_response)
        return mock_response
