from __future__ import annotations

import argparse
import os
import sys

from bot.client import BinanceFuturesClient
from bot.exceptions import BinanceAPIError, NetworkError, ValidationError
from bot.logging_config import configure_logging
from bot.orders import place_order
from bot.validators import validate_order_inputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET or LIMIT orders on Binance Futures Testnet",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair symbol, e.g., BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument(
        "--order-type",
        required=True,
        choices=["MARKET", "LIMIT"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Limit price (required for LIMIT orders)")
    parser.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures base URL",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path to log file",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run without real API calls and return mocked responses",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_file)

    try:
        validated = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")

        if not args.mock and (not api_key or not api_secret):
            raise ValidationError(
                "Missing BINANCE_API_KEY/BINANCE_API_SECRET in environment. "
                "Set credentials or use --mock."
            )

        client = BinanceFuturesClient(
            api_key=api_key or "mock-key",
            api_secret=api_secret or "mock-secret",
            base_url=args.base_url,
            mock_mode=args.mock,
        )
        response = place_order(client, validated)

        print("\n=== ORDER REQUEST SUMMARY ===")
        print(f"symbol: {validated['symbol']}")
        print(f"side: {validated['side']}")
        print(f"type: {validated['order_type']}")
        print(f"quantity: {validated['quantity']}")
        if validated["order_type"] == "LIMIT":
            print(f"price: {validated['price']}")

        print("\n=== ORDER RESPONSE ===")
        print(f"orderId: {response.get('orderId')}")
        print(f"status: {response.get('status')}")
        print(f"executedQty: {response.get('executedQty')}")
        avg_price = response.get("avgPrice")
        if avg_price is not None:
            print(f"avgPrice: {avg_price}")

        print("\n✅ Order placed successfully.")
        return 0

    except ValidationError as exc:
        print(f"❌ Validation error: {exc}")
        return 2
    except (BinanceAPIError, NetworkError) as exc:
        print(f"❌ Order failed: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
