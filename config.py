"""
Configuration for Market Data Service Test Framework
"""
import os

# Base URL for the market data service
BASE_URL = os.getenv("MARKET_DATA_SERVICE_URL", "http://localhost:3101")

# API Key for authentication
API_KEY = os.getenv("MARKET_DATA_API_KEY", "7fXZt817QOeBr4H2XH/mDmhKO+2yybe1prDYDSg4HOD8gC7qeiZBfscuZgtMnVOK")

# Timeout for API requests (in seconds)
REQUEST_TIMEOUT = 30

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1

# Test configuration - Updated to match actual service
# Symbol format uses no separator (e.g., BTCUSDT)
TEST_SYMBOLS = {
    "binance": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    "bitget": ["BTCUSDT", "ETHUSDT"],
    "kucoin": ["BTCUSDT", "ETHUSDT"],
    "aster": ["BTCUSDT", "ETHUSDT"],
    "hyperliquid": ["BTCUSDT", "ETHUSDT"],
    "weex": ["BTCUSDT", "ETHUSDT"],
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

# Tushare 测试配置（A股/港股/美股）
TUSHARE_CONFIG = {
    # A股测试股票
    "astock": {
        "symbols": ["000001.SZ", "600000.SH"],  # 平安银行、浦发银行
        "indices": ["000001.SH", "399001.SZ"],  # 上证指数、深证成指
        "intervals": ["daily", "weekly", "monthly"],
    },
    # 港股测试股票
    "hkstock": {
        "symbols": ["00700.HK", "00941.HK"],  # 腾讯控股、中国移动
    },
    # 美股测试股票
    "usstock": {
        "symbols": ["AAPL", "MSFT", "GOOGL"],  # 苹果、微软、谷歌
    },
}

# V2 Technical indicators (26 个，含 V1 已有的 11 个 + 新增 15 个)
V2_INDICATORS = [
    "sma", "ema", "rsi", "macd", "boll", "kdj", "atr", "obv", "cci", "adx", "vwap",
    "aroon", "sar", "trix", "ht_trendline", "stoch", "mom", "roc", "cmo",
    "ultosc", "ppo", "natr", "stddev", "ad", "mfi", "willr", "adosc",
]

# V2 指标默认参数 (key=指标名, value=query 参数字典)
V2_INDICATOR_PARAMS = {
    "sma":           {"period": 20},
    "ema":           {"period": 20},
    "rsi":           {"period": 14},
    "macd":          {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "boll":          {"period": 20, "nbdev": 2.0},
    "kdj":           {"fastk_period": 9, "slowk_period": 3, "slowd_period": 3},
    "atr":           {"period": 14},
    "obv":           {},
    "cci":           {"period": 14},
    "adx":           {"period": 14},
    "vwap":          {"period": 20},
    "aroon":         {"period": 14},
    "sar":           {"acceleration": 0.02, "maximum": 0.2},
    "trix":          {"period": 14},
    "ht_trendline":  {},
    "stoch":         {"k_period": 14, "d_period": 3, "smooth_period": 3},
    "mom":           {"period": 10},
    "roc":           {"period": 12},
    "cmo":           {"period": 14},
    "ultosc":        {"period1": 7, "period2": 14, "period3": 28},
    "ppo":           {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "natr":          {"period": 14},
    "stddev":        {"period": 20},
    "ad":            {},
    "mfi":           {"period": 14},
    "willr":         {"period": 14},
    "adosc":         {"fast_period": 3, "slow_period": 10},
}

# V2 市场测试配置 (2 个市场)
V2_MARKET_CONFIG = {
    "crypto": {
        "symbol": "BTCUSDT",
        "exchange": "binance",
        "interval": "1d",
    },
    "cn": {
        "symbol": "000001.SZ",
        "exchange": "",
        "interval": "1d",
    },
}

# Report output directory
REPORT_DIR = os.getenv("REPORT_DIR", "./reports")

# Enable verbose logging
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"
