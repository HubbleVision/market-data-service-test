"""
Configuration for Market Data Service Test Framework
"""
import os

# Base URL for the market data service
BASE_URL = os.getenv("MARKET_DATA_SERVICE_URL", "http://localhost:8080")

# API Key for authentication
API_KEY = os.getenv("MARKET_DATA_API_KEY", "hubble-market-data-2024")

# Timeout for API requests (in seconds)
REQUEST_TIMEOUT = 30

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1

# Test configuration - Updated to match actual service
# Symbol format uses "/" separator (e.g., BTC/USDT)
TEST_SYMBOLS = {
    "binance": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
    "bitget": ["BTC/USDT", "ETH/USDT"],
    "kucoin": ["BTC/USDT", "ETH/USDT"],
}

# K-line intervals supported by the service
KLINE_INTERVALS = [
    "1m", "5m", "15m", "1h", "4h", "1d", "1w"
]

# Technical indicators supported by the service
INDICATORS = [
    "sma",      # Simple Moving Average
    "ema",      # Exponential Moving Average
    "rsi",      # Relative Strength Index
    "macd",     # Moving Average Convergence Divergence
    "boll",     # Bollinger Bands (not "bbands")
    "kdj",      # KDJ Indicator
    "adx",      # Average Directional Index
    "atr",      # Average True Range
    "cci",      # Commodity Channel Index
    "vwap",     # Volume Weighted Average Price
    "obv",      # On-Balance Volume
]

# Report output directory
REPORT_DIR = os.getenv("REPORT_DIR", "./reports")

# Enable verbose logging
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"
