"""
Market Data Service API Client
Provides a unified interface for testing the market data service
Supports both V1 and V2 endpoints
"""
import requests
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from config import BASE_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, VERBOSE, API_KEY, REQUEST_INTERVAL


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

        # Rate limiting: wait between requests to avoid AV 5/min limit
        _last_request_time = getattr(self, '_last_request_time', 0)
        elapsed = time.time() - _last_request_time
        if elapsed < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed)

        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                self._last_request_time = start_time
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    self._log(f"Request OK: HTTP {response.status_code} ({response_time:.0f}ms)")
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

    # ==================== V1 K-Line (Candlestick) API ====================

    def get_kline(self, exchange: str, symbol: str, interval: str,
                  limit: Optional[int] = None,
                  start_time: Optional[str] = None,
                  end_time: Optional[str] = None) -> APIResponse:
        """Get K-line data (V1)"""
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

    # ==================== V1 Indicator API ====================

    def get_indicator(self, exchange: str, symbol: str, interval: str,
                      indicator: str, params: List = None,
                      limit: int = 500) -> APIResponse:
        """Get technical indicator data (V1 POST)"""
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
        """Get all supported indicators for a symbol (V1)"""
        from config import INDICATORS

        indicator_params = {
            "sma": [20], "ema": [20], "rsi": [14], "macd": [12, 26, 9],
            "boll": [20, 2.0, 2.0], "kdj": [9, 3, 3], "adx": [14],
            "atr": [14], "cci": [14], "vwap": [20], "obv": []
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
        """Get information about all supported indicators (V1)"""
        return self.get("/api/v1/indicators/info")

    # ==================== V2 Indicators API ====================

    def get_v2_indicator(self, indicator: str, market: str, symbol: str,
                         exchange: str = None, interval: str = None,
                         limit: int = None, start: str = None,
                         end: str = None, **extra_params) -> APIResponse:
        """V2 single indicator GET request"""
        params = {"market": market, "symbol": symbol, "interval": interval}
        if exchange:
            params["exchange"] = exchange
        if limit:
            params["limit"] = limit
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        params.update(extra_params)
        return self.get(f"/api/v2/indicators/{indicator}", params=params)

    def post_v2_indicators(self, market: str, symbol: str,
                           exchange: str = None, interval: str = None,
                           limit: int = None, start: str = None,
                           end: str = None,
                           indicators: List[Dict] = None) -> APIResponse:
        """V2 batch indicators POST request"""
        data = {
            "market": market,
            "symbol": symbol,
            "interval": interval,
            "indicators": indicators or [],
        }
        if exchange:
            data["exchange"] = exchange
        if limit:
            data["limit"] = limit
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        return self.post("/api/v2/indicators", data=data)

    def post_v2_indicators_batch(self, market: str, symbol: str,
                                  exchange: str = None, interval: str = None,
                                  limit: int = None, start: str = None,
                                  end: str = None,
                                  indicators: List[Dict] = None) -> APIResponse:
        """V2 batch indicators POST request (supports all four markets)"""
        data = {
            "market": market,
            "symbol": symbol,
            "interval": interval,
            "indicators": indicators or [],
        }
        if exchange:
            data["exchange"] = exchange
        if limit:
            data["limit"] = limit
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        return self.post("/api/v2/indicators/batch", data=data)

    # ==================== V2 Crypto Basic ====================

    def v2_get_kline(self, exchange: str, symbol: str, interval: str,
                     limit: Optional[int] = None, product_type: str = None,
                     start_time: str = None, end_time: str = None) -> APIResponse:
        """V2 unified K-line (DB -> Exchange -> CoinAnk fallback)"""
        params = {"exchange": exchange, "symbol": symbol, "interval": interval}
        if limit:
            params["limit"] = limit
        if product_type:
            params["productType"] = product_type
        if start_time:
            params["start"] = start_time
        if end_time:
            params["end"] = end_time
        return self.get("/api/v2/crypto/klines", params=params)

    def v2_get_exchanges(self) -> APIResponse:
        """V2 get supported exchanges"""
        return self.get("/api/v2/crypto/exchanges")

    def v2_get_symbols_list(self, exchange: str = None) -> APIResponse:
        """V2 get trading pairs list"""
        params = {}
        if exchange:
            params["exchange"] = exchange
        return self.get("/api/v2/crypto/symbols/list", params=params)

    # ==================== V2 Crypto Open Interest ====================

    def v2_get_oi_list(self, base_coin: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/list", params=_drop_none({"baseCoin": base_coin}))

    def v2_get_oi_history(self, exchange: str, symbol: str, interval: str,
                          end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/history",
                        params=_drop_none({"exchange": exchange, "symbol": symbol, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_oi_kline(self, exchange: str, symbol: str, interval: str,
                        end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/kline",
                        params=_drop_none({"exchange": exchange, "symbol": symbol, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_oi_agg_history(self, base_coin: str, interval: str,
                              end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/agg-history",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_oi_agg_kline(self, base_coin: str, interval: str,
                            end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/agg-kline",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_oi_coin_realtime(self, base_coin: str) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/coin-realtime", params={"baseCoin": base_coin})

    def v2_get_oi_vs_mc(self, base_coin: str, interval: str,
                        end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/open-interest/oi-vs-mc",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval, "endTime": end_time, "size": size}))

    # ==================== V2 Crypto Funding Rate ====================

    def v2_get_funding_realtime(self, type_: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/realtime", params=_drop_none({"type": type_}))

    def v2_get_funding_history(self, exchange: str, symbol: str, interval: str,
                               end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/history",
                        params=_drop_none({"exchange": exchange, "symbol": symbol, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_funding_cumulative(self, type_: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/cumulative", params=_drop_none({"type": type_}))

    def v2_get_funding_weighted(self, base_coin: str, interval: str,
                                end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/weighted",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_funding_kline(self, exchange: str, symbol: str, interval: str,
                             end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/kline",
                        params=_drop_none({"exchange": exchange, "symbol": symbol, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_funding_heatmap(self, type_: str, interval: str) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/heatmap", params={"type": type_, "interval": interval})

    def v2_get_funding_symbol_history(self, exchange: str, symbol: str, interval: str,
                                      end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/funding-rate/symbol-history",
                        params=_drop_none({"exchange": exchange, "symbol": symbol, "interval": interval, "endTime": end_time, "size": size}))

    # ==================== V2 Crypto Liquidation ====================

    def v2_get_liquidation_realtime(self, coin: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/realtime", params=_drop_none({"coin": coin}))

    def v2_get_liquidation_agg_history(self, coin: str, interval: str,
                                       end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/agg-history",
                        params=_drop_none({"coin": coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_liquidation_history(self, symbol: str, interval: str,
                                   end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/history",
                        params=_drop_none({"symbol": symbol, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_liquidation_orders(self, coin: str = None, interval: str = None,
                                  end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/orders",
                        params=_drop_none({"coin": coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_liquidation_map(self, coin: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/map", params=_drop_none({"coin": coin}))

    def v2_get_liquidation_heatmap(self, coin: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/heatmap", params=_drop_none({"coin": coin}))

    def v2_get_liquidation_agg_map(self, coin: str = None, interval: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/agg-map", params=_drop_none({"coin": coin, "interval": interval}))

    def v2_get_liquidation_heatmap_symbols(self) -> APIResponse:
        return self.get("/api/v2/crypto/liquidation/heatmap-symbols")

    # ==================== V2 Crypto Long/Short ====================

    def v2_get_long_short_exchange(self, base_coin: str, interval: str,
                                   end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/long-short/exchange",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_long_short_account(self, symbol: str, exchange: str, interval: str,
                                  end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/long-short/account",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_long_short_top_trader(self, symbol: str, exchange: str, interval: str,
                                     end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/long-short/top-trader",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_long_short_kline(self, type_: str, symbol: str, exchange: str, interval: str,
                                end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/long-short/kline",
                        params=_drop_none({"type": type_, "symbol": symbol, "exchange": exchange, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_long_short_taker_ratio(self, base_coin: str, interval: str,
                                      end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/long-short/taker-ratio",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_long_short_top_trader_account(self, symbol: str, exchange: str, interval: str,
                                             end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/long-short/top-trader-account",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval, "endTime": end_time, "size": size}))

    # ==================== V2 Crypto CVD ====================

    def v2_get_cvd_kline(self, symbol: str, exchange: str, interval: str,
                         product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/cvd/kline",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    # ==================== V2 Crypto Buy/Sell ====================

    def v2_get_buy_sell_count(self, symbol: str, exchange: str, interval: str,
                              product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/buy-sell/count",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    def v2_get_buy_sell_volume(self, symbol: str, exchange: str, interval: str,
                               product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/buy-sell/volume",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    def v2_get_buy_sell_amount(self, symbol: str, exchange: str, interval: str,
                               product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/buy-sell/amount",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    def v2_get_buy_sell_agg_count(self, base_coin: str, interval: str,
                                  product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/buy-sell/agg-count",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    def v2_get_buy_sell_agg_volume(self, base_coin: str, interval: str,
                                   product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/buy-sell/agg-volume",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    def v2_get_buy_sell_agg_amount(self, base_coin: str, interval: str,
                                   product_type: str = None, end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/buy-sell/agg-amount",
                        params=_drop_none({"baseCoin": base_coin, "interval": interval,
                                           "productType": product_type, "endTime": end_time, "size": size}))

    # ==================== V2 Crypto ETF ====================

    def v2_get_etf_btc(self) -> APIResponse:
        return self.get("/api/v2/crypto/etf/btc")

    def v2_get_etf_eth(self) -> APIResponse:
        return self.get("/api/v2/crypto/etf/eth")

    def v2_get_etf_btc_flow(self) -> APIResponse:
        return self.get("/api/v2/crypto/etf/btc-flow")

    def v2_get_etf_eth_flow(self) -> APIResponse:
        return self.get("/api/v2/crypto/etf/eth-flow")

    # ==================== V2 Crypto Indicators ====================

    def v2_get_crypto_indicator_fear_greed(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/fear-greed")

    def v2_get_crypto_indicator_ahr999(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/ahr999")

    def v2_get_crypto_indicator_two_year_ma(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/two-year-ma")

    def v2_get_crypto_indicator_btc_dominance(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/btc-dominance")

    def v2_get_crypto_indicator_puell(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/puell")

    def v2_get_crypto_indicator_pi_cycle(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/pi-cycle")

    def v2_get_crypto_indicator_altcoin_index(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/altcoin-index")

    def v2_get_crypto_indicator_grayscale(self) -> APIResponse:
        return self.get("/api/v2/crypto/indicator/grayscale")

    # ==================== V2 Crypto News ====================

    def v2_get_crypto_news_list(self, type_: str, lang: str, page: str, page_size: str,
                                is_popular: str, search: str) -> APIResponse:
        return self.get("/api/v2/crypto/news/list",
                        params={"type": type_, "lang": lang, "page": page,
                                "pageSize": page_size, "isPopular": is_popular, "search": search})

    def v2_get_crypto_news_detail(self, news_id: str) -> APIResponse:
        return self.get("/api/v2/crypto/news/detail", params={"id": news_id})

    def v2_get_crypto_news_search(self, query: str, lang: str = None,
                                   page: int = None, page_size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/news/search",
                        params=_drop_none({"q": query, "lang": lang,
                                           "page": page, "pageSize": page_size}))

    def v2_get_crypto_news_latest(self, type_: str = None, lang: str = None,
                                   page_size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/news/latest",
                        params=_drop_none({"type": type_, "lang": lang, "pageSize": page_size}))

    # ==================== V2 Crypto Whale ====================

    def v2_get_whale_positions(self, size: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/whale/positions", params=_drop_none({"size": size}))

    def v2_get_whale_activity(self, size: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/whale/activity", params=_drop_none({"size": size}))

    # ==================== V2 Crypto Large Order ====================

    def v2_get_large_order_market(self, symbol: str, product_type: str, amount: str,
                                  end_time: str = None, size: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/large-order/market",
                        params=_drop_none({"symbol": symbol, "productType": product_type, "amount": amount,
                                           "endTime": end_time, "size": size}))

    def v2_get_large_order_limit(self, symbol: str, exchange_type: str, is_history: str,
                                 amount: str = None, exchange: str = None, side: str = None,
                                 start_time: str = None, size: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/large-order/limit",
                        params=_drop_none({"symbol": symbol, "exchangeType": exchange_type, "isHistory": is_history,
                                           "amount": amount, "exchange": exchange, "side": side,
                                           "startTime": start_time, "size": size}))

    # ==================== V2 Crypto Ranking ====================

    def v2_get_ranking_open_interest(self) -> APIResponse:
        return self.get("/api/v2/crypto/ranking/open-interest")

    def v2_get_ranking_volume(self) -> APIResponse:
        return self.get("/api/v2/crypto/ranking/volume")

    def v2_get_ranking_price_change(self) -> APIResponse:
        return self.get("/api/v2/crypto/ranking/price-change")

    def v2_get_ranking_liquidation(self) -> APIResponse:
        return self.get("/api/v2/crypto/ranking/liquidation")

    # ==================== V2 Crypto Order Book ====================

    def v2_get_order_book_by_symbol(self, symbol: str, exchange: str, interval: str,
                                    product_type: str = None, rate: str = None,
                                    end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/order-book/by-symbol",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "rate": rate, "endTime": end_time, "size": size}))

    def v2_get_order_book_by_exchange(self, symbol: str, exchange: str, interval: str,
                                      product_type: str = None, rate: str = None,
                                      base_coin: str = None, end_time: str = None,
                                      size: int = None, type_: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/order-book/by-exchange",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "rate": rate, "baseCoin": base_coin,
                                           "endTime": end_time, "size": size, "type": type_}))

    def v2_get_order_book_heatmap(self, symbol: str, exchange: str, interval: str,
                                  end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/order-book/heatmap",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "endTime": end_time, "size": size}))

    # ==================== V2 Crypto Order Flow ====================

    def v2_get_order_flow_lists(self, symbol: str, exchange: str, interval: str,
                                product_type: str = None, tick_count: str = None,
                                end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/order-flow/lists",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "productType": product_type, "tickCount": tick_count,
                                           "endTime": end_time, "size": size}))

    # ==================== V2 Crypto Capital Flow ====================

    def v2_get_capital_flow_realtime(self, product_type: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/capital-flow/realtime", params=_drop_none({"productType": product_type}))

    def v2_get_capital_flow_history(self, base_coin: str, product_type: str, interval: str,
                                    end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/capital-flow/history",
                        params=_drop_none({"baseCoin": base_coin, "productType": product_type,
                                           "interval": interval, "endTime": end_time, "size": size}))

    def v2_get_net_positions(self, symbol: str, exchange: str, interval: str,
                             end_time: str = None, size: int = None) -> APIResponse:
        return self.get("/api/v2/crypto/net-positions",
                        params=_drop_none({"symbol": symbol, "exchange": exchange, "interval": interval,
                                           "endTime": end_time, "size": size}))

    # ==================== V2 Crypto Market Overview ====================

    def v2_get_crypto_coins(self) -> APIResponse:
        return self.get("/api/v2/crypto/coins")

    def v2_get_crypto_price(self, symbol: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/price", params=_drop_none({"symbol": symbol}))

    def v2_get_crypto_marketcap(self, coin: str = None) -> APIResponse:
        return self.get("/api/v2/crypto/marketcap", params=_drop_none({"coin": coin}))

    def v2_get_crypto_futures(self) -> APIResponse:
        return self.get("/api/v2/crypto/futures")

    # ==================== V2 Crypto RSI Screener ====================

    def v2_get_crypto_rsi_screener(self, interval: str, exchange: str) -> APIResponse:
        return self.get("/api/v2/crypto/rsi/screener", params={"interval": interval, "exchange": exchange})

    # ==================== V2 Crypto Proxy ====================

    def v2_get_crypto_proxy(self, endpoint_path: str, **params) -> APIResponse:
        return self.get(f"/api/v2/crypto/proxy/{endpoint_path}", params=params)

    # ==================== V2 CNStock ====================

    def v2_get_cnstock_symbols(self, list_status: str = "L") -> APIResponse:
        return self.get("/api/v2/cnstock/symbols", params={"listStatus": list_status})

    def v2_get_cnstock_klines(self, symbol: str, interval: str = "daily",
                              start_date: str = None, end_date: str = None,
                              limit: int = 100) -> APIResponse:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/stocks", params=params)

    def v2_get_cnstock_company(self, ts_code: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        return self.get("/api/v2/cnstock/company", params=params)

    def v2_get_cnstock_daily_basic(self, ts_code: str = None, trade_date: str = None,
                                   start_date: str = None, end_date: str = None,
                                   limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/daily-basic", params=params)

    def v2_get_cnstock_adj_factor(self, ts_code: str = None, start_date: str = None,
                                  end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/adj-factor", params=params)

    def v2_get_cnstock_name_change(self, ts_code: str = None, start_date: str = None,
                                   end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/name-change", params=params)

    def v2_get_cnstock_new_share(self, start_date: str = None, end_date: str = None,
                                 limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/new-share", params=params)

    def v2_get_cnstock_stk_limit(self, ts_code: str = None, trade_date: str = None,
                                 start_date: str = None, end_date: str = None,
                                 limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/stk-limit", params=params)

    def v2_get_cnstock_suspend(self, ts_code: str = None, start_date: str = None,
                               end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/suspend", params=params)

    def v2_get_cnstock_trade_cal(self, exchange: str = None, start_date: str = None,
                                 end_date: str = None, limit: int = 1000) -> APIResponse:
        params = {"limit": limit}
        if exchange:
            params["exchange"] = exchange
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/trade-cal", params=params)

    # ==================== V2 CNStock Index ====================

    def v2_get_cnstock_index_basic(self, market: str = None) -> APIResponse:
        params = {}
        if market:
            params["market"] = market
        return self.get("/api/v2/cnstock/index/basic", params=params)

    def v2_get_cnstock_index_daily(self, ts_code: str, start_date: str = None,
                                   end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/index/daily", params=params)

    def v2_get_cnstock_index_weekly(self, ts_code: str, start_date: str = None,
                                    end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/index/weekly", params=params)

    def v2_get_cnstock_index_monthly(self, ts_code: str, start_date: str = None,
                                     end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/index/monthly", params=params)

    def v2_get_cnstock_index_daily_basic(self, ts_code: str = None, start_date: str = None,
                                         end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/index/daily-basic", params=params)

    def v2_get_cnstock_index_weight(self, index_code: str = None, start_date: str = None,
                                    end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if index_code:
            params["indexCode"] = index_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/cnstock/index/weight", params=params)

    def v2_get_cnstock_index_classify(self, src: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if src:
            params["src"] = src
        return self.get("/api/v2/cnstock/index/classify", params=params)

    # ==================== V2 CNStock Finance ====================

    def v2_get_finance_income(self, ts_code: str = None, period: str = None,
                              start_date: str = None, end_date: str = None,
                              limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/income", params=params)

    def v2_get_finance_balancesheet(self, ts_code: str = None, period: str = None,
                                     start_date: str = None, end_date: str = None,
                                     limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/balancesheet", params=params)

    def v2_get_finance_cashflow(self, ts_code: str = None, period: str = None,
                                start_date: str = None, end_date: str = None,
                                limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/cashflow", params=params)

    def v2_get_finance_indicator(self, ts_code: str = None, period: str = None,
                                 start_date: str = None, end_date: str = None,
                                 limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/indicator", params=params)

    def v2_get_finance_forecast(self, ts_code: str = None, period: str = None,
                                start_date: str = None, end_date: str = None,
                                limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/forecast", params=params)

    def v2_get_finance_express(self, ts_code: str = None, period: str = None,
                               start_date: str = None, end_date: str = None,
                               limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/express", params=params)

    def v2_get_finance_dividend(self, ts_code: str = None, start_date: str = None,
                                end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/dividend", params=params)

    def v2_get_finance_disclosure_date(self, ts_code: str = None, period: str = None,
                                       start_date: str = None, end_date: str = None,
                                       limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/disclosure-date", params=params)

    def v2_get_finance_main_bz(self, ts_code: str = None, period: str = None,
                               type_name: str = None, start_date: str = None,
                               end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if type_name: params["typeName"] = type_name
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/finance/main-bz", params=params)

    # ==================== V2 CNStock Holders ====================

    def v2_get_holders_top10(self, ts_code: str, period: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/holders/top10", params=params)

    def v2_get_holders_float_top10(self, ts_code: str, period: str = None,
                                   start_date: str = None, end_date: str = None,
                                   limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/holders/float-top10", params=params)

    def v2_get_holders_number(self, ts_code: str, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/holders/number", params=params)

    # ==================== V2 CNStock MoneyFlow ====================

    def v2_get_moneyflow_hsgt(self, start_date: str = None, end_date: str = None,
                              limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/moneyflow/hsgt", params=params)

    def v2_get_moneyflow_hsgt_top10(self, start_date: str = None, end_date: str = None,
                                    limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/moneyflow/hsgt-top10", params=params)

    def v2_get_moneyflow_margin(self, start_date: str = None, end_date: str = None,
                                limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/moneyflow/margin", params=params)

    def v2_get_moneyflow_margin_detail(self, ts_code: str = None, start_date: str = None,
                                       end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/moneyflow/margin-detail", params=params)

    def v2_get_moneyflow_stock(self, ts_code: str = None, start_date: str = None,
                               end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/moneyflow/stock", params=params)

    # ==================== V2 CNStock Reference ====================

    def v2_get_repurchase(self, ts_code: str = None, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/repurchase", params=params)

    def v2_get_block_trade(self, ts_code: str = None, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/block-trade", params=params)

    def v2_get_share_float(self, ts_code: str = None, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/share-float", params=params)

    def v2_get_pledge(self, ts_code: str = None, start_date: str = None,
                      end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/pledge", params=params)

    def v2_get_pledge_stat(self, ts_code: str = None, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/pledge-stat", params=params)

    # ==================== V2 Fund ====================

    def v2_get_fund_basic(self, market: str = None, fund_type: str = None,
                          limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if market: params["market"] = market
        if fund_type: params["fundType"] = fund_type
        return self.get("/api/v2/fund/basic", params=params)

    def v2_get_fund_nav(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/fund/nav", params=params)

    def v2_get_fund_daily(self, ts_code: str = None, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/fund/daily", params=params)

    def v2_get_fund_portfolio(self, ts_code: str = None, period: str = None,
                              limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        return self.get("/api/v2/fund/portfolio", params=params)

    def v2_get_fund_etf_basic(self, limit: int = 100) -> APIResponse:
        return self.get("/api/v2/fund/etf-basic", params={"limit": limit})

    def v2_get_fund_share(self, ts_code: str = None, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/fund/share", params=params)

    def v2_get_fund_div(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/fund/div", params=params)

    def v2_get_fund_manager(self, ts_code: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        return self.get("/api/v2/fund/manager", params=params)

    def v2_get_fund_company(self, limit: int = 100) -> APIResponse:
        return self.get("/api/v2/fund/company", params={"limit": limit})

    # ==================== V2 CNStock Macro ====================

    def v2_get_macro_shibor(self, start_date: str = None, end_date: str = None,
                            limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/macro/shibor", params=params)

    def v2_get_macro_lpr(self, start_date: str = None, end_date: str = None,
                         limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/macro/lpr", params=params)

    def v2_get_macro_cpi(self, start_date: str = None, end_date: str = None,
                         limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/macro/cpi", params=params)

    def v2_get_macro_ppi(self, start_date: str = None, end_date: str = None,
                         limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/macro/ppi", params=params)

    def v2_get_macro_gdp(self, start_date: str = None, end_date: str = None,
                         limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/macro/gdp", params=params)

    def v2_get_macro_money_supply(self, start_date: str = None, end_date: str = None,
                                  limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v2/cnstock/macro/money-supply", params=params)

    # ==================== V2 HKStock ====================

    def v2_get_hkstock_symbols(self, list_status: str = "L") -> APIResponse:
        return self.get("/api/v2/hkstock/symbols", params={"listStatus": list_status})

    def v2_get_hkstock_daily(self, symbol: str, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"symbol": symbol, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/hkstock/stocks", params=params)

    def v2_get_hkstock_trade_cal(self, start_date: str = None, end_date: str = None,
                                  limit: int = 1000) -> APIResponse:
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/hkstock/trade-cal", params=params)

    def v2_get_hkstock_ggt_top10(self, trade_date: str = None, ts_code: str = None,
                                  start_date: str = None, end_date: str = None,
                                  limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if trade_date:
            params["tradeDate"] = trade_date
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/hkstock/ggt-top10", params=params)

    def v2_get_hkstock_ggt_daily(self, trade_date: str = None, start_date: str = None,
                                  end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/hkstock/ggt-daily", params=params)

    def v2_get_hkstock_hold(self, ts_code: str = None, trade_date: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/hkstock/hold", params=params)

    # ==================== V2 Securities (Real-time Quote) ====================

    def v2_get_market_quote(self, market: str, codes: str, fields: str = None) -> APIResponse:
        """V2 unified market quote — routes to per-market securities endpoint"""
        market_map = {"hk": "hkstock", "cn": "cnstock", "us": "usstock"}
        market_path = market_map.get(market, f"{market}stock")
        params = {"codes": codes}
        if fields:
            params["fields"] = fields
        return self.get(f"/api/v2/{market_path}/securities", params=params)

    def v2_get_hkstock_securities(self, codes: str, fields: str = None) -> APIResponse:
        params = {"codes": codes}
        if fields:
            params["fields"] = fields
        return self.get("/api/v2/hkstock/securities", params=params)

    def v2_get_cnstock_securities(self, codes: str, fields: str = None) -> APIResponse:
        params = {"codes": codes}
        if fields:
            params["fields"] = fields
        return self.get("/api/v2/cnstock/securities", params=params)

    def v2_get_usstock_securities(self, codes: str, fields: str = None) -> APIResponse:
        params = {"codes": codes}
        if fields:
            params["fields"] = fields
        return self.get("/api/v2/usstock/securities", params=params)

    # ==================== V2 Fuxin Market Data ====================

    def v2_fuxin_min(self, market: str, code: str, ktype: str = None) -> APIResponse:
        """Fuxin minute-level time-series data (min1/min5)"""
        params = {"code": code}
        if ktype:
            params["ktype"] = ktype
        return self.get(f"/api/v2/{market}/min", params=params)

    def v2_fuxin_brokerq(self, market: str, code: str) -> APIResponse:
        """Fuxin 5-level broker queue (bid/ask)"""
        return self.get(f"/api/v2/{market}/brokerq", params={"code": code})

    def v2_fuxin_orderbook(self, market: str, code: str) -> APIResponse:
        """Fuxin 10-level order book (bid/ask)"""
        return self.get(f"/api/v2/{market}/orderbook", params={"code": code})

    def v2_fuxin_tick(self, market: str, code: str, last_time: str = None,
                      count: int = None) -> APIResponse:
        """Fuxin tick-by-tick trade data"""
        params = {"code": code}
        if last_time:
            params["lastTime"] = last_time
        if count:
            params["count"] = count
        return self.get(f"/api/v2/{market}/tick", params=params)

    # ==================== V2 USStock ====================

    def v2_get_usstock_symbols(self) -> APIResponse:
        return self.get("/api/v2/usstock/symbols")

    def v2_get_usstock_daily(self, symbol: str, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"symbol": symbol, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/usstock/stocks", params=params)

    def v2_get_usstock_trade_cal(self, start_date: str = None, end_date: str = None,
                                  limit: int = 1000) -> APIResponse:
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v2/usstock/trade-cal", params=params)

    # ==================== V1 Tushare Stock API (legacy) ====================

    def get_astock_symbols(self, list_status: str = "L") -> APIResponse:
        params = {"listStatus": list_status}
        return self.get("/api/v1/stock/astock/symbols", params=params)

    def get_astock_klines(self, symbol: str, interval: str = "daily",
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> APIResponse:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/klines", params=params)

    def get_index_basic(self, market: str = None) -> APIResponse:
        params = {}
        if market:
            params["market"] = market
        return self.get("/api/v1/stock/astock/index/basic", params=params)

    def get_index_daily(self, ts_code: str, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/daily", params=params)

    def get_hkstock_symbols(self, list_status: str = "L") -> APIResponse:
        return self.get("/api/v1/stock/hkstock/symbols", params={"listStatus": list_status})

    def get_hkstock_daily(self, symbol: str, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"symbol": symbol, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/daily", params=params)

    def get_usstock_symbols(self) -> APIResponse:
        return self.get("/api/v1/stock/usstock/symbols")

    def get_usstock_daily(self, symbol: str, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"symbol": symbol, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/usstock/daily", params=params)

    # ==================== V1 Finance API (legacy) ====================

    def get_finance_income(self, ts_code: str = None, period: str = None,
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/income", params=params)

    def get_finance_balancesheet(self, ts_code: str = None, period: str = None,
                                 start_date: str = None, end_date: str = None,
                                 limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/balancesheet", params=params)

    def get_finance_cashflow(self, ts_code: str = None, period: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/cashflow", params=params)

    def get_finance_indicator(self, ts_code: str = None, period: str = None,
                              start_date: str = None, end_date: str = None,
                              limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/indicator", params=params)

    def get_finance_forecast(self, ts_code: str = None, period: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/forecast", params=params)

    def get_finance_dividend(self, ts_code: str = None, start_date: str = None,
                             end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/dividend", params=params)

    def get_finance_express(self, ts_code: str = None, period: str = None,
                            start_date: str = None, end_date: str = None,
                            limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/express", params=params)

    def get_finance_disclosure_date(self, ts_code: str = None, period: str = None,
                                    start_date: str = None, end_date: str = None,
                                    limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/disclosure-date", params=params)

    def get_finance_main_bz(self, ts_code: str = None, period: str = None,
                            type_name: str = None, start_date: str = None,
                            end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        if type_name: params["typeName"] = type_name
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/main-bz", params=params)

    # ==================== V1 Fund API (legacy) ====================

    def get_fund_basic(self, market: str = None, fund_type: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if market: params["market"] = market
        if fund_type: params["fundType"] = fund_type
        return self.get("/api/v1/stock/fund/basic", params=params)

    def get_fund_nav(self, ts_code: str = None, start_date: str = None,
                     end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/nav", params=params)

    def get_fund_daily(self, ts_code: str = None, start_date: str = None,
                       end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/daily", params=params)

    def get_fund_portfolio(self, ts_code: str = None, period: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if period: params["period"] = period
        return self.get("/api/v1/stock/fund/portfolio", params=params)

    def get_fund_etf_basic(self, limit: int = 100) -> APIResponse:
        return self.get("/api/v1/stock/fund/etf-basic", params={"limit": limit})

    def get_fund_share(self, ts_code: str = None, start_date: str = None,
                       end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/share", params=params)

    def get_fund_div(self, ts_code: str = None, start_date: str = None,
                     end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/div", params=params)

    def get_fund_manager(self, ts_code: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        return self.get("/api/v1/stock/fund/manager", params=params)

    def get_fund_company(self, limit: int = 100) -> APIResponse:
        return self.get("/api/v1/stock/fund/company", params={"limit": limit})

    # ==================== V1 Reference API (legacy) ====================

    def get_holders_top10(self, ts_code: str, period: str = None,
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/holders/top10", params=params)

    def get_holders_float_top10(self, ts_code: str, period: str = None,
                                start_date: str = None, end_date: str = None,
                                limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if period: params["period"] = period
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/holders/float-top10", params=params)

    def get_holders_number(self, ts_code: str, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/holders/number", params=params)

    def get_repurchase(self, ts_code: str = None, start_date: str = None,
                       end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/repurchase", params=params)

    def get_block_trade(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/block-trade", params=params)

    def get_share_float(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/share-float", params=params)

    def get_pledge(self, ts_code: str = None, start_date: str = None,
                   end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/pledge", params=params)

    def get_pledge_stat(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/pledge-stat", params=params)

    # ==================== V1 Macro API (legacy) ====================

    def get_macro_shibor(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/shibor", params=params)

    def get_macro_lpr(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/lpr", params=params)

    def get_macro_cpi(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/cpi", params=params)

    def get_macro_ppi(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/ppi", params=params)

    def get_macro_gdp(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/gdp", params=params)

    def get_macro_money(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/money", params=params)

    # ==================== V1 MoneyFlow API (legacy) ====================

    def get_moneyflow_hsgt(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/hsgt", params=params)

    def get_moneyflow_hsgt_top10(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/hsgt-top10", params=params)

    def get_moneyflow_margin(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/margin", params=params)

    def get_moneyflow_margin_detail(self, ts_code: str = None, start_date: str = None,
                                    end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/margin-detail", params=params)

    def get_moneyflow_stock(self, ts_code: str = None, start_date: str = None,
                            end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/stock", params=params)

    # ==================== V1 Stock Extension (legacy) ====================

    def get_astock_company(self, ts_code: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        return self.get("/api/v1/stock/astock/company", params=params)

    def get_astock_name_change(self, ts_code: str = None, start_date: str = None,
                               end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/name-change", params=params)

    def get_astock_new_share(self, start_date: str = None, end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/new-share", params=params)

    def get_astock_stk_limit(self, ts_code: str = None, trade_date: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if trade_date: params["tradeDate"] = trade_date
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/stk-limit", params=params)

    def get_astock_suspend(self, ts_code: str = None, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/suspend", params=params)

    def get_astock_trade_cal(self, exchange: str = None, start_date: str = None,
                             end_date: str = None, limit: int = 1000) -> APIResponse:
        params = {"limit": limit}
        if exchange: params["exchange"] = exchange
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/trade-cal", params=params)

    def get_astock_daily_basic(self, ts_code: str = None, trade_date: str = None,
                               start_date: str = None, end_date: str = None,
                               limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if trade_date: params["tradeDate"] = trade_date
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/daily-basic", params=params)

    def get_astock_adj_factor(self, ts_code: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/adj-factor", params=params)

    # ==================== V1 Index Extension (legacy) ====================

    def get_index_weekly(self, ts_code: str, start_date: str = None,
                         end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/weekly", params=params)

    def get_index_monthly(self, ts_code: str, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"tsCode": ts_code, "limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/monthly", params=params)

    def get_index_daily_basic(self, ts_code: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/daily-basic", params=params)

    def get_index_weight(self, index_code: str = None, start_date: str = None,
                         end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if index_code: params["indexCode"] = index_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/weight", params=params)

    def get_index_classify(self, src: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if src: params["src"] = src
        return self.get("/api/v1/stock/astock/index/classify", params=params)

    # ==================== V1 HK Extension (legacy) ====================

    def get_hkstock_trade_cal(self, start_date: str = None, end_date: str = None, limit: int = 1000) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/trade-cal", params=params)

    def get_hkstock_ggt_top10(self, trade_date: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if trade_date: params["tradeDate"] = trade_date
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/ggt-top10", params=params)

    def get_hkstock_ggt_daily(self, trade_date: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if trade_date: params["tradeDate"] = trade_date
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/ggt-daily", params=params)

    def get_hkstock_hold(self, ts_code: str = None, start_date: str = None,
                         end_date: str = None, limit: int = 100) -> APIResponse:
        params = {"limit": limit}
        if ts_code: params["tsCode"] = ts_code
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/hold", params=params)

    # ==================== V1 US Extension (legacy) ====================

    def get_usstock_trade_cal(self, start_date: str = None, end_date: str = None, limit: int = 1000) -> APIResponse:
        params = {"limit": limit}
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self.get("/api/v1/stock/usstock/trade-cal", params=params)

    # ==================== V2 Alpha Vantage Extended ====================

    def v2_av_market_status(self) -> APIResponse:
        """美股市场开收盘状态"""
        return self.get("/api/v2/usstock/market-status")

    def v2_av_top_gainers_losers(self, direction: str = None) -> APIResponse:
        """涨跌排行 (top_gainers / top_losers / most_actively_traded)"""
        params = _drop_none({"direction": direction})
        return self.get("/api/v2/usstock/top-movers", params=params)

    def v2_av_daily_adjusted(self, symbol: str, limit: int = 100) -> APIResponse:
        """复权日 K 线"""
        return self.get("/api/v2/usstock/stocks", params={"symbol": symbol, "limit": limit, "adjusted": "true"})

    def v2_av_weekly_adjusted(self, symbol: str, limit: int = 100) -> APIResponse:
        """复权周 K 线 (V2 无 weekly 路由，复用 daily+adjusted)"""
        return self.get("/api/v2/usstock/stocks", params={"symbol": symbol, "limit": limit, "adjusted": "true"})

    def v2_av_monthly_adjusted(self, symbol: str, limit: int = 100) -> APIResponse:
        """复权月 K 线 (V2 无 monthly 路由，复用 daily+adjusted)"""
        return self.get("/api/v2/usstock/stocks", params={"symbol": symbol, "limit": limit, "adjusted": "true"})

    def v2_av_income_statement(self, symbol: str) -> APIResponse:
        """利润表"""
        return self.get("/api/v2/usstock/finance/income", params={"symbol": symbol})

    def v2_av_balance_sheet(self, symbol: str) -> APIResponse:
        """资产负债表"""
        return self.get("/api/v2/usstock/finance/balancesheet", params={"symbol": symbol})

    def v2_av_cash_flow(self, symbol: str) -> APIResponse:
        """现金流量表"""
        return self.get("/api/v2/usstock/finance/cashflow", params={"symbol": symbol})

    def v2_av_earnings_estimates(self, symbol: str) -> APIResponse:
        """每股收益预估"""
        return self.get("/api/v2/usstock/finance/forecast", params={"symbol": symbol})

    def v2_av_dividends(self, symbol: str) -> APIResponse:
        """历史股息"""
        return self.get("/api/v2/usstock/finance/dividend", params={"symbol": symbol})

    def v2_av_splits(self, symbol: str) -> APIResponse:
        """历史拆股"""
        return self.get("/api/v2/usstock/finance/splits", params={"symbol": symbol})

    def v2_av_shares_outstanding(self, symbol: str) -> APIResponse:
        """流通股数量"""
        return self.get("/api/v2/usstock/finance/shares", params={"symbol": symbol})

    def v2_av_etf_profile(self, symbol: str) -> APIResponse:
        """ETF 档案"""
        return self.get("/api/v2/usstock/etf-profile", params={"symbol": symbol})

    def v2_av_earnings_calendar(self, horizon: str = "3month") -> APIResponse:
        """盈利日历"""
        return self.get("/api/v2/usstock/calendar/earnings", params={"horizon": horizon})

    def v2_av_ipo_calendar(self) -> APIResponse:
        """IPO 日历"""
        return self.get("/api/v2/usstock/calendar/ipo")

    def v2_av_fx_weekly(self, from_currency: str, to_currency: str, limit: int = 100) -> APIResponse:
        """外汇周线 — V2 index/klines 不支持货币对，此方法无效"""
        return APIResponse(success=False, status_code=0, data=None,
                           error="FX has no V2 route (index/klines only supports index symbols)", response_time_ms=0)

    def v2_av_fx_monthly(self, from_currency: str, to_currency: str, limit: int = 100) -> APIResponse:
        """外汇月线 — V2 index/klines 不支持货币对，此方法无效"""
        return APIResponse(success=False, status_code=0, data=None,
                           error="FX has no V2 route (index/klines only supports index symbols)", response_time_ms=0)

    def v2_av_crypto_weekly(self, symbol: str = "BTC", market: str = "USD", limit: int = 100) -> APIResponse:
        """加密货币周线 (V2 crypto klines with interval=1w)"""
        pair = f"{symbol}{market}T" if market == "USD" else f"{symbol}{market}"
        return self.get("/api/v2/crypto/klines", params={"exchange": "binance", "symbol": pair, "interval": "1w", "limit": limit})

    def v2_av_insider_transactions(self, symbol: str) -> APIResponse:
        """内部交易"""
        return self.get("/api/v2/usstock/finance/insider", params={"symbol": symbol})

    def v2_av_institutional_holdings(self, symbol: str) -> APIResponse:
        """机构持仓"""
        return self.get("/api/v2/usstock/finance/institutional", params={"symbol": symbol})

    # --- 商品 (专用端点) ---
    def v2_av_commodity(self, function_name: str) -> APIResponse:
        """通用商品端点"""
        return self.get(f"/api/v2/commodity/{function_name}")

    def v2_av_gold_silver_spot(self) -> APIResponse:
        """贵金属现货"""
        return self.get("/api/v2/commodity/spot")

    def v2_av_gold_silver_history(self, interval: str = "daily", limit: int = 100) -> APIResponse:
        """贵金属历史 K 线"""
        return self.get("/api/v2/commodity/klines", params={"symbol": "GOLD", "interval": interval})

    # --- 指数 ---
    def v2_av_index_data(self, symbol: str, interval: str = "daily", limit: int = 100) -> APIResponse:
        """指数数据"""
        return self.get("/api/v2/index/klines", params={"symbol": symbol, "interval": interval, "limit": limit})

    def v2_av_index_catalog(self) -> APIResponse:
        """指数目录"""
        return self.get("/api/v2/index/symbols")

    def close(self):
        """Close the session"""
        self.session.close()


# ==================== Helper ====================

def _drop_none(d: dict) -> dict:
    """Remove keys with None values"""
    return {k: v for k, v in d.items() if v is not None}
