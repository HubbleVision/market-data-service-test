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

    # ==================== V2 Indicator API ====================

    def get_v2_indicator(self, indicator: str, market: str, symbol: str,
                         exchange: str = None, interval: str = None,
                         limit: int = None, start: str = None,
                         end: str = None, **extra_params) -> APIResponse:
        """
        V2 单指标 GET 请求

        Args:
            indicator: 指标名 (ma, ema, rsi, macd, ...)
            market: 市场类型 (crypto, cn, hk, us)
            symbol: 股票代码或交易对
            exchange: 交易所 (仅 crypto 市场需要)
            interval: K 线周期
            limit: 数据条数
            start: 开始日期 YYYY-MM-DD
            end: 结束日期 YYYY-MM-DD
            **extra_params: 指标特有参数 (period, fast_period, ...)
        """
        params = {
            "market": market,
            "symbol": symbol,
            "interval": interval,
        }
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
        """
        V2 批量指标 POST 请求

        Args:
            market: 市场类型 (crypto, cn, hk, us)
            symbol: 股票代码或交易对
            exchange: 交易所 (仅 crypto 市场需要)
            interval: K 线周期
            limit: 数据条数
            start: 开始日期 YYYY-MM-DD
            end: 结束日期 YYYY-MM-DD
            indicators: 指标列表，如 [{"type": "ma", "params": [20]}]
        """
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

    # ==================== Tushare Stock API ====================

    def get_astock_symbols(self, list_status: str = "L") -> APIResponse:
        """
        获取A股股票列表

        Args:
            list_status: 上市状态 L=上市 D=退市 P=暂停上市
        """
        return self.get("/api/v1/stock/astock/symbols", params={"listStatus": list_status})

    def get_astock_klines(self, symbol: str, interval: str = "daily",
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> APIResponse:
        """
        获取A股K线数据

        Args:
            symbol: 股票代码，如 000001.SZ
            interval: 周期 daily/weekly/monthly
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 数量限制
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/klines", params=params)

    def get_index_basic(self, market: str = None) -> APIResponse:
        """
        获取指数基本信息

        Args:
            market: 市场代码 SSE=上交所 SZSE=深交所
        """
        params = {}
        if market:
            params["market"] = market
        return self.get("/api/v1/stock/astock/index/basic", params=params)

    def get_index_daily(self, ts_code: str, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        """
        获取指数日线数据

        Args:
            ts_code: 指数代码，如 000001.SH
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 数量限制
        """
        params = {
            "tsCode": ts_code,
            "limit": limit
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/daily", params=params)

    def get_hkstock_symbols(self, list_status: str = "L") -> APIResponse:
        """
        获取港股股票列表

        Args:
            list_status: 上市状态 L=上市 D=退市
        """
        return self.get("/api/v1/stock/hkstock/symbols", params={"listStatus": list_status})

    def get_hkstock_daily(self, symbol: str, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        """
        获取港股日线数据

        Args:
            symbol: 港股代码，如 00700.HK
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 数量限制
        """
        params = {
            "symbol": symbol,
            "limit": limit
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/daily", params=params)

    def get_usstock_symbols(self) -> APIResponse:
        """获取美股股票列表"""
        return self.get("/api/v1/stock/usstock/symbols")

    def get_usstock_daily(self, symbol: str, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        """
        获取美股日线数据

        Args:
            symbol: 美股代码，如 AAPL
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 数量限制
        """
        params = {
            "symbol": symbol,
            "limit": limit
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/usstock/daily", params=params)

    # ==================== Finance API (财务数据) ====================

    def get_finance_income(self, ts_code: str = None, period: str = None,
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> APIResponse:
        """
        获取利润表数据

        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 数量限制
        """
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/income", params=params)

    def get_finance_balancesheet(self, ts_code: str = None, period: str = None,
                                 start_date: str = None, end_date: str = None,
                                 limit: int = 100) -> APIResponse:
        """获取资产负债表数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/balancesheet", params=params)

    def get_finance_cashflow(self, ts_code: str = None, period: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        """获取现金流量表数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/cashflow", params=params)

    def get_finance_indicator(self, ts_code: str = None, period: str = None,
                              start_date: str = None, end_date: str = None,
                              limit: int = 100) -> APIResponse:
        """获取财务指标数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/indicator", params=params)

    def get_finance_forecast(self, ts_code: str = None, period: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        """获取业绩预告数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/forecast", params=params)

    def get_finance_dividend(self, ts_code: str = None, start_date: str = None,
                             end_date: str = None, limit: int = 100) -> APIResponse:
        """获取分红送股数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/dividend", params=params)

    def get_finance_express(self, ts_code: str = None, period: str = None,
                            start_date: str = None, end_date: str = None,
                            limit: int = 100) -> APIResponse:
        """获取业绩快报数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/express", params=params)

    # ==================== Fund API (基金数据) ====================

    def get_fund_basic(self, market: str = None, fund_type: str = None,
                       limit: int = 100) -> APIResponse:
        """获取基金列表"""
        params = {"limit": limit}
        if market:
            params["market"] = market
        if fund_type:
            params["fundType"] = fund_type
        return self.get("/api/v1/stock/fund/basic", params=params)

    def get_fund_nav(self, ts_code: str = None, start_date: str = None,
                     end_date: str = None, limit: int = 100) -> APIResponse:
        """获取基金净值数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/nav", params=params)

    def get_fund_daily(self, ts_code: str = None, start_date: str = None,
                       end_date: str = None, limit: int = 100) -> APIResponse:
        """获取ETF日线行情数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/daily", params=params)

    def get_fund_portfolio(self, ts_code: str = None, period: str = None,
                           limit: int = 100) -> APIResponse:
        """获取基金持仓数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        return self.get("/api/v1/stock/fund/portfolio", params=params)

    # ==================== Reference API (参考数据) ====================

    def get_holders_top10(self, ts_code: str, period: str = None,
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> APIResponse:
        """获取前十大股东数据"""
        params = {"tsCode": ts_code, "limit": limit}
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/holders/top10", params=params)

    def get_holders_float_top10(self, ts_code: str, period: str = None,
                                start_date: str = None, end_date: str = None,
                                limit: int = 100) -> APIResponse:
        """获取前十大流通股东数据"""
        params = {"tsCode": ts_code, "limit": limit}
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/holders/float-top10", params=params)

    def get_holders_number(self, ts_code: str, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        """获取股东人数数据"""
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/holders/number", params=params)

    def get_repurchase(self, ts_code: str = None, start_date: str = None,
                       end_date: str = None, limit: int = 100) -> APIResponse:
        """获取股票回购数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/repurchase", params=params)

    def get_block_trade(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        """获取大宗交易数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/block-trade", params=params)

    def get_share_float(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        """获取限售股解禁数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/share-float", params=params)

    def get_pledge(self, ts_code: str = None, start_date: str = None,
                   end_date: str = None, limit: int = 100) -> APIResponse:
        """获取股权质押数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/pledge", params=params)

    # ==================== Macro API (宏观经济) ====================

    def get_macro_shibor(self, start_date: str = None, end_date: str = None,
                         limit: int = 100) -> APIResponse:
        """获取Shibor利率数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/shibor", params=params)

    def get_macro_lpr(self, start_date: str = None, end_date: str = None,
                      limit: int = 100) -> APIResponse:
        """获取LPR利率数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/lpr", params=params)

    def get_macro_cpi(self, start_date: str = None, end_date: str = None,
                      limit: int = 100) -> APIResponse:
        """获取CPI居民消费价格指数数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/cpi", params=params)

    def get_macro_ppi(self, start_date: str = None, end_date: str = None,
                      limit: int = 100) -> APIResponse:
        """获取PPI工业生产者价格指数数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/ppi", params=params)

    def get_macro_gdp(self, start_date: str = None, end_date: str = None,
                      limit: int = 100) -> APIResponse:
        """获取GDP国内生产总值数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/gdp", params=params)

    def get_macro_money(self, start_date: str = None, end_date: str = None,
                        limit: int = 100) -> APIResponse:
        """获取货币供应量数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/macro/money", params=params)

    # ==================== MoneyFlow API (资金流向) ====================

    def get_moneyflow_hsgt(self, start_date: str = None, end_date: str = None,
                           limit: int = 100) -> APIResponse:
        """获取沪深港通资金流向数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/hsgt", params=params)

    def get_moneyflow_hsgt_top10(self, start_date: str = None, end_date: str = None,
                                 limit: int = 100) -> APIResponse:
        """获取沪深股通十大成交股数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/hsgt-top10", params=params)

    def get_moneyflow_margin(self, start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        """获取融资融券汇总数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/margin", params=params)

    def get_moneyflow_margin_detail(self, ts_code: str = None, start_date: str = None,
                                    end_date: str = None, limit: int = 100) -> APIResponse:
        """获取融资融券明细数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/margin-detail", params=params)

    def get_moneyflow_stock(self, ts_code: str = None, start_date: str = None,
                            end_date: str = None, limit: int = 100) -> APIResponse:
        """获取个股资金流向数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/moneyflow/stock", params=params)

    # ==================== A股扩展接口 ====================

    def get_astock_company(self, ts_code: str = None, limit: int = 100) -> APIResponse:
        """获取上市公司基本信息"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        return self.get("/api/v1/stock/astock/company", params=params)

    def get_astock_name_change(self, ts_code: str = None, start_date: str = None,
                               end_date: str = None, limit: int = 100) -> APIResponse:
        """获取股票曾用名"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/name-change", params=params)

    def get_astock_new_share(self, start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        """获取IPO新股上市数据"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/new-share", params=params)

    def get_astock_stk_limit(self, ts_code: str = None, trade_date: str = None,
                             start_date: str = None, end_date: str = None,
                             limit: int = 100) -> APIResponse:
        """获取每日涨跌停价格"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/stk-limit", params=params)

    def get_astock_suspend(self, ts_code: str = None, start_date: str = None,
                           end_date: str = None, limit: int = 100) -> APIResponse:
        """获取停复牌信息"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/suspend", params=params)

    def get_astock_trade_cal(self, exchange: str = None, start_date: str = None,
                             end_date: str = None, limit: int = 1000) -> APIResponse:
        """获取交易日历"""
        params = {"limit": limit}
        if exchange:
            params["exchange"] = exchange
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/trade-cal", params=params)

    def get_astock_daily_basic(self, ts_code: str = None, trade_date: str = None,
                               start_date: str = None, end_date: str = None,
                               limit: int = 100) -> APIResponse:
        """获取每日指标"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/daily-basic", params=params)

    def get_astock_adj_factor(self, ts_code: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        """获取复权因子"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/adj-factor", params=params)

    # ==================== 指数扩展接口 ====================

    def get_index_weekly(self, ts_code: str, start_date: str = None,
                         end_date: str = None, limit: int = 100) -> APIResponse:
        """获取指数周线数据"""
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/weekly", params=params)

    def get_index_monthly(self, ts_code: str, start_date: str = None,
                          end_date: str = None, limit: int = 100) -> APIResponse:
        """获取指数月线数据"""
        params = {"tsCode": ts_code, "limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/monthly", params=params)

    def get_index_daily_basic(self, ts_code: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        """获取指数每日指标"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/daily-basic", params=params)

    def get_index_weight(self, index_code: str = None, start_date: str = None,
                         end_date: str = None, limit: int = 100) -> APIResponse:
        """获取指数成分权重"""
        params = {"limit": limit}
        if index_code:
            params["indexCode"] = index_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/index/weight", params=params)

    def get_index_classify(self, src: str = None, limit: int = 100) -> APIResponse:
        """获取申万行业分类"""
        params = {"limit": limit}
        if src:
            params["src"] = src
        return self.get("/api/v1/stock/astock/index/classify", params=params)

    # ==================== 港股扩展接口 ====================

    def get_hkstock_trade_cal(self, start_date: str = None, end_date: str = None,
                              limit: int = 1000) -> APIResponse:
        """获取港股交易日历"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/trade-cal", params=params)

    def get_hkstock_ggt_top10(self, trade_date: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        """获取港股通十大成交股"""
        params = {"limit": limit}
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/ggt-top10", params=params)

    def get_hkstock_ggt_daily(self, trade_date: str = None, start_date: str = None,
                              end_date: str = None, limit: int = 100) -> APIResponse:
        """获取港股通每日成交数据"""
        params = {"limit": limit}
        if trade_date:
            params["tradeDate"] = trade_date
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/ggt-daily", params=params)

    def get_hkstock_hold(self, ts_code: str = None, start_date: str = None,
                         end_date: str = None, limit: int = 100) -> APIResponse:
        """获取沪深股通持股明细"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/hkstock/hold", params=params)

    # ==================== 美股扩展接口 ====================

    def get_usstock_trade_cal(self, start_date: str = None, end_date: str = None,
                              limit: int = 1000) -> APIResponse:
        """获取美股交易日历"""
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/usstock/trade-cal", params=params)

    # ==================== 财务扩展接口 ====================

    def get_finance_disclosure_date(self, ts_code: str = None, period: str = None,
                                    start_date: str = None, end_date: str = None,
                                    limit: int = 100) -> APIResponse:
        """获取财报披露日期"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/disclosure-date", params=params)

    def get_finance_main_bz(self, ts_code: str = None, period: str = None,
                            type_name: str = None, start_date: str = None,
                            end_date: str = None, limit: int = 100) -> APIResponse:
        """获取主营业务构成"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if period:
            params["period"] = period
        if type_name:
            params["typeName"] = type_name
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/finance/main-bz", params=params)

    # ==================== 基金扩展接口 ====================

    def get_fund_etf_basic(self, limit: int = 100) -> APIResponse:
        """获取ETF列表"""
        return self.get("/api/v1/stock/fund/etf-basic", params={"limit": limit})

    def get_fund_share(self, ts_code: str = None, start_date: str = None,
                       end_date: str = None, limit: int = 100) -> APIResponse:
        """获取基金份额数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/share", params=params)

    def get_fund_div(self, ts_code: str = None, start_date: str = None,
                     end_date: str = None, limit: int = 100) -> APIResponse:
        """获取基金分红数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/fund/div", params=params)

    def get_fund_manager(self, ts_code: str = None, limit: int = 100) -> APIResponse:
        """获取基金经理数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        return self.get("/api/v1/stock/fund/manager", params=params)

    def get_fund_company(self, limit: int = 100) -> APIResponse:
        """获取基金公司数据"""
        return self.get("/api/v1/stock/fund/company", params={"limit": limit})

    # ==================== 参考数据扩展接口 ====================

    def get_pledge_stat(self, ts_code: str = None, start_date: str = None,
                        end_date: str = None, limit: int = 100) -> APIResponse:
        """获取股权质押统计数据"""
        params = {"limit": limit}
        if ts_code:
            params["tsCode"] = ts_code
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.get("/api/v1/stock/astock/pledge-stat", params=params)

    def close(self):
        """Close the session"""
        self.session.close()
