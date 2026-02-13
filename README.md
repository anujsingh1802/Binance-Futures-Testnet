# Binance Futures Testnet Trading Bot (Python)

A simplified CLI trading bot that places **MARKET** and **LIMIT** orders on **Binance Futures Testnet (USDT-M)** using direct REST calls.

## Features

- Place MARKET and LIMIT orders
- Support BUY and SELL
- CLI input with validation
- Structured modules:
  - API client layer (`bot/client.py`)
  - Order logic (`bot/orders.py`)
  - Validation (`bot/validators.py`)
  - Logging setup (`bot/logging_config.py`)
  - CLI entry (`cli.py`)
- Logs API requests, responses, and errors to a file
- Handles validation, Binance API, and network exceptions
- `--mock` mode for local testing without API credentials

## Setup

1. **Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set credentials**

```bash
export BINANCE_API_KEY="your_testnet_key"
export BINANCE_API_SECRET="your_testnet_secret"
```

> Base URL used by default: `https://testnet.binancefuture.com`

## Usage Examples

### MARKET order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001
```

### LIMIT order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type LIMIT \
  --quantity 0.001 \
  --price 70000
```

### Local test run (no real API call)

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001 \
  --mock
```

## Log Files

- Default log file: `logs/trading_bot.log`
- Sample logs included:
  - `logs/market_order.log`
  - `logs/limit_order.log`

## Assumptions

- This bot targets **USDT-M Futures Testnet** only.
- Quantity/price precision and symbol-specific exchange filters are not pre-fetched from exchange metadata; Binance validates these server-side.
- For interview portability, sample logs are generated with `--mock` mode in environments without keys.

