"""
CoinAnk API Test Module
Tests for CoinAnk integration endpoints
"""
import time
from typing import Dict, List, Optional
from test_base import BaseTester, TestResult, TestStatus
from api_client import APIClient


def get_one_day_ago_timestamp_ms():
    """获取一天前的时间戳(毫秒)"""
    one_day_ago = time.time() - 24 * 60 * 60  # 当前时间减去一天
    return str(int(one_day_ago * 1000))


def get_one_day_ago_timestamp_s():
    """获取一天前的时间戳(秒)"""
    one_day_ago = time.time() - 24 * 60 * 60
    return str(int(one_day_ago))


# 兼容旧函数名，返回一天前的时间戳
def get_current_timestamp_ms():
    """获取一天前的时间戳(毫秒) - 用于API请求"""
    return get_one_day_ago_timestamp_ms()


class CoinAnkTester(BaseTester):
    """Test CoinAnk API endpoints"""

    # CoinAnk endpoints to test - Updated to match backend enabled endpoints
    ENDPOINTS = {
        # ========== 已屏蔽的接口（后端未启用） ==========
        # Basic endpoints - DISABLED
        # "coins": {"path": "/api/v1/coinank/coins", "params": {}, "disabled": True, "reason": "后端已屏蔽"},
        # "symbols": {"path": "/api/v1/coinank/symbols", "params": {"type": "contract"}, "disabled": True, "reason": "后端已屏蔽"},
        # "price": {"path": "/api/v1/coinank/price", "params": {"symbol": "BTCUSDT"}, "disabled": True, "reason": "后端已屏蔽"},
        # "marketcap": {"path": "/api/v1/coinank/marketcap", "params": {"coin": "BTC"}, "disabled": True, "reason": "后端已屏蔽"},
        # "futures": {"path": "/api/v1/coinank/futures", "params": {}, "disabled": True, "reason": "后端已屏蔽"},

        # Liquidation - DISABLED
        # "liquidation_realtime": {"path": "/api/v1/coinank/liquidation/realtime", "params": {"coin": "BTC"}, "disabled": True, "reason": "后端已屏蔽"},
        # "liquidation_history": {"path": "/api/v1/coinank/liquidation/history", "params": {"symbol": "BTCUSDT"}, "disabled": True, "reason": "后端已屏蔽"},
        # "liquidation_agg_history": {"path": "/api/v1/coinank/liquidation/agg-history", "params": {"coin": "BTC"}, "disabled": True, "reason": "后端已屏蔽"},

        # ========== 持仓数据 ==========
        "open_interest_list": {"path": "/api/v1/coinank/open-interest/list", "params": {"baseCoin": "BTC"}},
        # open_interest_history 不需要 exchange 参数，只需要 symbol 和 interval
        "open_interest_history": {"path": "/api/v1/coinank/open-interest/history", "params": {"exchange": "Binance", "symbol": "BTCUSDT", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "open_interest_kline": {"path": "/api/v1/coinank/open-interest/kline", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "open_interest_agg_history": {"path": "/api/v1/coinank/open-interest/agg-history", "params": {"baseCoin": "BTC", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "open_interest_agg_kline": {"path": "/api/v1/coinank/open-interest/agg-kline", "params": {"baseCoin": "BTC", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "open_interest_coin_realtime": {"path": "/api/v1/coinank/open-interest/coin-realtime", "params": {"baseCoin": "BTC"}},
        "open_interest_oi_vs_mc": {"path": "/api/v1/coinank/open-interest/oi-vs-mc", "params": {"baseCoin": "BTC", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},

        # ========== 资金费率 ==========
        "funding_rate_realtime": {"path": "/api/v1/coinank/funding-rate/realtime", "params": {"type": "current"}},
        # funding_rate_history 需要动态生成 endTime，在测试时动态处理
        "funding_rate_cumulative": {"path": "/api/v1/coinank/funding-rate/cumulative", "params": {"type": "day"}},
        # funding_rate_weighted 需要 baseCoin, interval, endTime，动态处理
        "funding_rate_kline": {"path": "/api/v1/coinank/funding-rate/kline", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "funding_rate_heatmap": {"path": "/api/v1/coinank/funding-rate/heatmap", "params": {"type": "marketCap", "interval": "1M"}},
        "funding_rate_symbol_history": {"path": "/api/v1/coinank/funding-rate/symbol-history", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},

        # ========== 多空比 ==========
        "long_short_exchange": {"path": "/api/v1/coinank/long-short/exchange", "params": {"baseCoin": "BTC", "productType": "SWAP"}},
        "long_short_account": {"path": "/api/v1/coinank/long-short/account", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "long_short_top_trader": {"path": "/api/v1/coinank/long-short/top-trader", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        # long_short_kline 需要 type 参数 (longShortPerson/longShortPosition/longShortAccount)
        "long_short_kline": {"path": "/api/v1/coinank/long-short/kline", "params": {"type": "longShortPerson", "symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "long_short_taker_ratio": {"path": "/api/v1/coinank/long-short/taker-ratio", "params": {"baseCoin": "BTC", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "long_short_top_trader_account": {"path": "/api/v1/coinank/long-short/top-trader-account", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},

        # ========== CVD/市价单 ==========
        "cvd_kline": {"path": "/api/v1/coinank/cvd/kline", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        # cvd_agg 需要 exchanges 参数(空字符串表示聚合所有交易所)，不是 baseCoin
        "cvd_agg": {"path": "/api/v1/coinank/cvd/agg", "params": {"exchanges": "", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "buy_sell_count": {"path": "/api/v1/coinank/buy-sell/count", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "buy_sell_volume": {"path": "/api/v1/coinank/buy-sell/volume", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "buy_sell_amount": {"path": "/api/v1/coinank/buy-sell/amount", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "buy_sell_agg_count": {"path": "/api/v1/coinank/buy-sell/agg-count", "params": {"baseCoin": "BTC", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "buy_sell_agg_volume": {"path": "/api/v1/coinank/buy-sell/agg-volume", "params": {"baseCoin": "BTC", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "buy_sell_agg_amount": {"path": "/api/v1/coinank/buy-sell/agg-amount", "params": {"baseCoin": "BTC", "interval": "1h", "productType": "SWAP", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},

        # ========== K线 ==========
        "kline": {"path": "/api/v1/coinank/kline", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h"}},

        # ========== 指标数据 ==========
        "indicator_fear_greed": {"path": "/api/v1/coinank/indicator/fear-greed", "params": {}},
        "indicator_ahr999": {"path": "/api/v1/coinank/indicator/ahr999", "params": {}},
        "indicator_btc_dominance": {"path": "/api/v1/coinank/indicator/btc-dominance", "params": {}},
        "indicator_puell": {"path": "/api/v1/coinank/indicator/puell", "params": {}},
        "indicator_pi_cycle": {"path": "/api/v1/coinank/indicator/pi-cycle", "params": {}},
        "indicator_two_year_ma": {"path": "/api/v1/coinank/indicator/two-year-ma", "params": {}},
        "indicator_altcoin_index": {"path": "/api/v1/coinank/indicator/altcoin-index", "params": {}},
        "indicator_grayscale": {"path": "/api/v1/coinank/indicator/grayscale", "params": {}},

        # ========== ETF ==========
        "etf_btc": {"path": "/api/v1/coinank/etf/btc", "params": {}},
        "etf_eth": {"path": "/api/v1/coinank/etf/eth", "params": {}},
        "etf_btc_flow": {"path": "/api/v1/coinank/etf/btc-flow", "params": {}},
        "etf_eth_flow": {"path": "/api/v1/coinank/etf/eth-flow", "params": {}},

        # ========== 新闻快讯 ==========
        "news_list": {"path": "/api/v1/coinank/news/list", "params": {"size": "10"}},
        # "news_detail": {"path": "/api/v1/coinank/news/detail", "params": {"id": "1"}},  # 需要有效的新闻ID

        # ========== HyperLiquid 鲸鱼 ==========
        "whale_positions": {"path": "/api/v1/coinank/whale/positions", "params": {"size": "10"}},
        "whale_activity": {"path": "/api/v1/coinank/whale/activity", "params": {"size": "10"}},

        # ========== 大额订单 ==========
        "large_order_market": {"path": "/api/v1/coinank/large-order/market", "params": {"symbol": "BTCUSDT", "exchange": "Binance"}},
        "large_order_limit": {"path": "/api/v1/coinank/large-order/limit", "params": {"symbol": "BTCUSDT", "exchange": "Binance"}},

        # ========== 热门排行 ==========
        "ranking_open_interest": {"path": "/api/v1/coinank/ranking/open-interest", "params": {}},
        "ranking_volume": {"path": "/api/v1/coinank/ranking/volume", "params": {}},
        "ranking_price_change": {"path": "/api/v1/coinank/ranking/price-change", "params": {}},
        "ranking_liquidation": {"path": "/api/v1/coinank/ranking/liquidation", "params": {}},

        # ========== 订单本 ==========
        # order_book_by_symbol 需要interval参数
        "order_book_by_symbol": {"path": "/api/v1/coinank/order-book/by-symbol", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "rate": "0.01", "productType": "SWAP", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        # order_book_by_exchange 需要interval参数
        "order_book_by_exchange": {"path": "/api/v1/coinank/order-book/by-exchange", "params": {"baseCoin": "BTC", "productType": "SWAP", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        # order_book_heatmap interval只支持1m/3m/5m
        "order_book_heatmap": {"path": "/api/v1/coinank/order-book/heatmap", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1m", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},

        # ========== 订单流 ==========
        # order_flow_lists 需要interval参数，tickCount是必填
        "order_flow_lists": {"path": "/api/v1/coinank/order-flow/lists", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "productType": "SWAP", "tickCount": "1", "endTime": get_one_day_ago_timestamp_ms()}},

        # ========== 资金流/净头寸 ==========
        # ========== 资金流/净头寸 ==========
        "capital_flow_realtime": {"path": "/api/v1/coinank/capital-flow/realtime", "params": {"productType": "SWAP"}},
        # capital_flow_history interval是必填参数
        "capital_flow_history": {"path": "/api/v1/coinank/capital-flow/history", "params": {"baseCoin": "BTC", "productType": "SWAP", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
        "net_positions": {"path": "/api/v1/coinank/net-positions", "params": {"symbol": "BTCUSDT", "exchange": "Binance", "interval": "1h", "endTime": get_one_day_ago_timestamp_ms(), "size": 10}},
    }

    # 已屏蔽的接口列表（用于报告）
    DISABLED_ENDPOINTS = {
        # 币种与基础行情
        "coins": {"reason": "后端已屏蔽 - 接口有问题"},
        "symbols": {"reason": "后端已屏蔽 - 接口有问题"},
        "price": {"reason": "后端已屏蔽 - 接口有问题"},
        "marketcap": {"reason": "后端已屏蔽 - 接口有问题"},
        "futures": {"reason": "后端已屏蔽 - 接口有问题"},
        # 爆仓与清算数据
        "liquidation_realtime": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_agg_history": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_history": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_orders": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_map": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_heatmap": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_agg_map": {"reason": "后端已屏蔽 - 套餐限制"},
        "liquidation_heatmap_symbols": {"reason": "后端已屏蔽 - 套餐限制"},
    }

    def __init__(self, base_url: str = None):
        super().__init__(base_url)

    def test_endpoint(self, name: str, endpoint_config: Dict) -> TestResult:
        """Test a single CoinAnk endpoint"""
        start_time = time.time()

        result = TestResult(
            test_name=f"coinank_{name}",
            category="CoinAnk"
        )

        try:
            response = self.client.get(endpoint_config["path"], params=endpoint_config.get("params", {}))
            elapsed_ms = (time.time() - start_time) * 1000
            result.response_time_ms = elapsed_ms

            if response.success:
                # Check if response has valid data
                data = response.data
                # CoinAnk API 返回格式: {"code": "0", "msg": "success", "data": {...}}
                # 或者直接返回数据对象
                if data:
                    # 检查 CoinAnk 标准响应格式
                    api_success = data.get("code") == "0" or data.get("msg") == "success" or data.get("success") == True

                    if api_success:
                        # 检查 data 字段是否有实际内容
                        response_data = data.get("data")

                        # 判断数据是否有效
                        has_valid_data = False
                        data_info = ""

                        if response_data is not None:
                            if isinstance(response_data, list):
                                has_valid_data = len(response_data) > 0
                                data_info = f"array[{len(response_data)}]"
                            elif isinstance(response_data, dict):
                                has_valid_data = len(response_data) > 0
                                data_info = f"object({len(response_data)} keys)"
                            else:
                                # 其他类型（字符串、数字等）
                                has_valid_data = True
                                data_info = str(type(response_data).__name__)

                        if has_valid_data:
                            result.status = TestStatus.PASSED
                            result.message = f"Success - {data_info}"
                        else:
                            result.status = TestStatus.FAILED
                            result.message = f"Empty data - {data_info}"
                            result.error_details = str(data)[:500]

                        result.response_data = data  # 保存完整响应用于调试
                    elif response.status_code == 204:
                        result.status = TestStatus.PASSED
                        result.message = "Success (No Content)"
                    else:
                        # 打印完整响应以便调试
                        result.status = TestStatus.FAILED
                        error_msg = data.get("msg") or data.get("detail") or data.get("error") or "Unknown error"
                        result.message = f"API returned error: {error_msg}"
                        result.error_details = str(data)[:500]  # 限制长度
                else:
                    result.status = TestStatus.FAILED
                    result.message = "Empty response"
                    result.error_details = "Response data is empty"
            else:
                result.status = TestStatus.FAILED
                result.message = f"HTTP {response.status_code}: {response.error}"
                result.error_details = response.error

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            result.response_time_ms = elapsed_ms
            result.status = TestStatus.ERROR
            result.message = f"Exception: {str(e)[:100]}"
            result.error_details = str(e)

        return result

    def run_all_tests(self) -> Dict:
        """Run all CoinAnk tests"""
        self.start_test_run()

        # Log disabled endpoints
        self._log(f"\n=== 已屏蔽的接口 (共 {len(self.DISABLED_ENDPOINTS)} 个) ===")
        for name, info in self.DISABLED_ENDPOINTS.items():
            self._log(f"  [SKIP] {name}: {info['reason']}")

        self._log(f"\n=== 开始测试启用的接口 (共 {len(self.ENDPOINTS)} 个) ===")

        for name, config in self.ENDPOINTS.items():
            result = self.test_endpoint(name, config)
            self._record_result(result)
            status_icon = "✓" if result.status == TestStatus.PASSED else "✗"
            self._log(f"  [{status_icon}] Test {name}: {result.status.value} - {result.message}")

        self.end_test_run()

        return {
            "summary": {
                "total": self.summary.total_tests,
                "passed": self.summary.passed,
                "failed": self.summary.failed,
                "errors": self.summary.errors,
                "success_rate": self.summary.success_rate,
                "disabled_count": len(self.DISABLED_ENDPOINTS)
            },
            "disabled_endpoints": self.DISABLED_ENDPOINTS,
            "results": [r.to_dict() for r in self.results]
        }

    def run_category_tests(self, category: str) -> Dict:
        """Run tests for a specific category"""
        category_endpoints = {
            "open_interest": [k for k in self.ENDPOINTS if k.startswith("open_interest")],
            "funding_rate": [k for k in self.ENDPOINTS if k.startswith("funding_rate")],
            "long_short": [k for k in self.ENDPOINTS if k.startswith("long_short")],
            "cvd": [k for k in self.ENDPOINTS if k.startswith("cvd") or k.startswith("buy_sell")],
            "indicator": [k for k in self.ENDPOINTS if k.startswith("indicator")],
            "etf": [k for k in self.ENDPOINTS if k.startswith("etf")],
            "whale": [k for k in self.ENDPOINTS if k.startswith("whale")],
            "ranking": [k for k in self.ENDPOINTS if k.startswith("ranking")],
            "order": [k for k in self.ENDPOINTS if k.startswith("order_") or k.startswith("large_order")],
            "capital": [k for k in self.ENDPOINTS if k.startswith("capital") or k.startswith("net_positions")],
        }

        if category not in category_endpoints:
            self._log(f"Unknown category: {category}")
            return {"error": f"Unknown category: {category}"}

        self.start_test_run()
        endpoints = category_endpoints[category]

        self._log(f"\n=== Testing {category} endpoints ({len(endpoints)} tests) ===")

        for name in endpoints:
            config = self.ENDPOINTS[name]
            result = self.test_endpoint(name, config)
            self._record_result(result)
            status_icon = "✓" if result.status == TestStatus.PASSED else "✗"
            self._log(f"  [{status_icon}] Test {name}: {result.status.value} - {result.message}")

        self.end_test_run()

        return {
            "category": category,
            "summary": {
                "total": self.summary.total_tests,
                "passed": self.summary.passed,
                "failed": self.summary.failed,
                "errors": self.summary.errors,
                "success_rate": self.summary.success_rate
            },
            "results": [r.to_dict() for r in self.results]
        }


def run_coinank_tests():
    """Run CoinAnk tests and generate report"""
    tester = CoinAnkTester()
    try:
        results = tester.run_all_tests()
        report_path = tester.generate_report("coinank_test_report")
        return results, report_path
    finally:
        tester.close()


if __name__ == "__main__":
    results, report_path = run_coinank_tests()
    print(f"\nReport saved to: {report_path}")
