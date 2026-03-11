"""
Market Data Service API Client
Provides a unified interface for testing the market data service
"""
import requests
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from config import BASE_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, VERBOSE, API_KEY


class ExchangeType(Enum):
    """Supported exchanges"""
    BINANCE = "binance"
    BITGET = "bitget"
    KUCOIN = "kucoin"


@dataclass
class APIResponse:
    """Standard API response wrapper"""
    success: bool
    status_code: int
    data: Optional[Any]
    error: Optional[str]
    response_time_ms: float

    def __bool__(self):
        return self.success


class APIClient:
    """Client for interacting with the Market Data Service"""

    def __init__(self, base_url: str = BASE_URL, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": self.api_key
        })

    def _log(self, message: str):
        """Log message if verbose mode is enabled"""
        if VERBOSE:
            print(f"[API] {message}")

    def _make_request(self, method: str, endpoint: str,
                      params: Optional[Dict] = None,
                      data: Optional[Dict] = None) -> APIResponse:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    return APIResponse(
                        success=True,
                        status_code=response.status_code,
                        data=response.json(),
                        error=None,
                        response_time_ms=response_time
                    )
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    self._log(f"Request failed: {error_msg}")
                    return APIResponse(
                        success=False,
                        status_code=response.status_code,
                        data=None,
                        error=error_msg,
                        response_time_ms=response_time
                    )

            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {REQUEST_TIMEOUT}s"
                self._log(f"Timeout on attempt {attempt + 1}/{MAX_RETRIES}")
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)[:100]}"
                self._log(f"Connection error on attempt {attempt + 1}/{MAX_RETRIES}")
            except Exception as e:
                last_error = f"Unexpected error: {str(e)[:100]}"
                self._log(f"Error on attempt {attempt + 1}/{MAX_RETRIES}: {e}")

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

        return APIResponse(
            success=False,
            status_code=0,
            data=None,
            error=last_error or "Unknown error",
            response_time_ms=0
        )

    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """Make GET request"""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> APIResponse:
        """Make POST request"""
        return self._make_request("POST", endpoint, data=data)

    # ==================== Service Discovery ====================

    def health_check(self) -> APIResponse:
        """Check service health"""
        return self.get("/api/v1/health")

    def get_openapi_spec(self) -> APIResponse:
        """Get OpenAPI specification"""
        return self.get("/openapi.json")

    def get_supported_exchanges(self) -> APIResponse:
        """Get list of supported exchanges"""
        return self.get("/api/v1/exchanges")

    def get_exchange_symbols(self, exchange: str) -> APIResponse:
        """Get available trading symbols for an exchange"""
        return self.get("/api/v1/symbols", params={"exchange": exchange})

    # ==================== K-Line (Candlestick) API ====================

    def get_kline(self, exchange: str, symbol: str, interval: str,
                  limit: Optional[int] = None,
                  start_time: Optional[str] = None,
                  end_time: Optional[str] = None) -> APIResponse:
        """
        Get K-line (candlestick) data

        Args:
            exchange: Exchange name (e.g., 'binance', 'bitget', 'kucoin')
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            interval: K-line interval (e.g., '1m', '1h', '1d')
            limit: Number of candles to return
            start_time: Start time (RFC3339 format)
            end_time: End time (RFC3339 format)
        """
        params = {
            "exchange": exchange,
            "symbol": symbol,
            "interval": interval
        }
        if limit:
            params["limit"] = limit
        if start_time:
            params["start"] = start_time
        if end_time:
            params["end"] = end_time

        return self.get("/api/v1/klines", params=params)

    def get_exchanges_kline(self, symbol: str, interval: str) -> Dict[str, APIResponse]:
        """Get K-line data from all exchanges"""
        results = {}
        for exchange in ExchangeType:
            results[exchange.value] = self.get_kline(
                exchange=exchange.value,
                symbol=symbol,
                interval=interval,
                limit=10
            )
        return results

    # ==================== Indicator API ====================

    def get_indicator(self, exchange: str, symbol: str, interval: str,
                      indicator: str, params: List = None,
                      limit: int = 500) -> APIResponse:
        """
        Get technical indicator data

        Args:
            exchange: Exchange name
            symbol: Trading pair symbol
            interval: K-line interval
            indicator: Indicator name (e.g., 'sma', 'rsi', 'macd')
            params: Indicator parameters (e.g., [20] for SMA period)
            limit: Number of K-lines to use for calculation
        """
        if params is None:
            params = []

        request_data = {
            "exchange": exchange,
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
            "indicators": [
                {
                    "type": indicator,
                    "params": params
                }
            ]
        }

        return self.post("/api/v1/indicators/technical", data=request_data)

    def get_all_indicators(self, exchange: str, symbol: str,
                           interval: str) -> Dict[str, APIResponse]:
        """Get all supported indicators for a symbol"""
        from config import INDICATORS

        # Default parameters for each indicator
        indicator_params = {
            "sma": [20],
            "ema": [20],
            "rsi": [14],
            "macd": [12, 26, 9],
            "boll": [20, 2.0, 2.0],
            "kdj": [9, 3, 3],
            "adx": [14],
            "atr": [14],
            "cci": [14],
            "vwap": [20],
            "obv": []
        }

        results = {}
        for indicator in INDICATORS:
            params = indicator_params.get(indicator, [])
            results[indicator] = self.get_indicator(
                exchange=exchange,
                symbol=symbol,
                interval=interval,
                indicator=indicator,
                params=params
            )
        return results

    def get_indicators_info(self) -> APIResponse:
        """Get information about all supported indicators"""
        return self.get("/api/v1/indicators/info")

    def close(self):
        """Close the session"""
        self.session.close()
