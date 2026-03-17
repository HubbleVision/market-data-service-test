#!/usr/bin/env python3
"""
CoinAnk 资金费率 API 测试脚本
测试新的 7 个资金费率接口
"""
import sys
import requests
from datetime import datetime
from typing import Dict, Any

from config import BASE_URL


class CoinAnkFundingRateTester:
    """CoinAnk 资金费率 API 测试"""

    def __init__(self, base_url: str = None):
        super().__init__(base_url or BASE_URL)
        self.test_results: Dict[str, Any] = {}
        self.session = requests.Session()

    def test_endpoint(self, method: str, endpoint: str, params: dict = None, **kwargs) -> Dict[str, Any]:
        """测试单个端点"""
        url = f"{self.base_url}{endpoint}"
        if params:
            url = f"{url}?{requests.utils.urlencode(params)}"

        start_time = time.time()
        response_time = time.time() - start_time
        response = self.session.get(url, method, timeout=30)

        try:
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": {}
                }
            json_data = response.json()
            return {
                "success": True,
                "message": "Success",
                "data": json_data,
                "response_time": response_time
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": {}
            }

    def test_hist_funding_rate(self) -> Dict[str, Any]:
        """测试历史结算资金费率接口"""
        endpoint = "/api/v1/coinank/funding-rate/history"
        params = {
            "baseCoin": "BTC",
            "exchangeType": "USDT",
            "size": 20
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def test_current_funding_rate(self) -> Dict[str, Any]:
        """测试实时资金费率接口"""
        endpoint = "/api/v1/coinank/funding-rate/current"
        params = {
            "type": "current"
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def test_accumulated_funding_rate(self) -> Dict[str, Any]:
        """测试累计资金费率接口"""
        endpoint = "/api/v1/coinank/funding-rate/accumulated"
        params = {
            "type": "day"
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def test_indicator_funding_rate(self) -> Dict[str, Any]:
        """测试交易对资金费率历史接口"""
        endpoint = "/api/v1/coinank/funding-rate/indicator"
        params = {
            "exchange": "Binance",
            "symbol": "BTCUSDT",
            "interval": "1h",
            "size": 10
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def test_kline_funding_rate(self) -> Dict[str, Any]:
        """测试交易对资金费率K线接口"""
        endpoint = "/api/v1/coinank/funding-rate/kline"
        params = {
            "exchange": "Binance",
            "symbol": "BTCUSDT",
            "interval": "1h",
            "size": 10
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def test_weighted_funding_rate(self) -> Dict[str, Any]:
        """测试加权资金费率接口"""
        endpoint = "/api/v1/coinank/funding-rate/weighted"
        params = {
            "baseCoin": "BTC",
            "interval": "1h",
            "endTime": str(int(datetime.now().timestamp() * 1000)),
            "size": 20
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def test_heatmap_funding_rate(self) -> Dict[str, Any]:
        """测试资金费率热力图接口"""
        endpoint = "/api/v1/coinank/funding-rate/heatmap"
        params = {
            "type": "marketCap",
            "interval": "1M"
        }
        return self.test_endpoint("GET", endpoint, params=params)

    def run_all_tests(self) -> bool:
        """运行所有资金费率测试"""
        print("\n" + "=" * 60)
        print("CoinAnk 资金费率 API 测试")
        print("=" * 60)
        print(f"服务地址: {self.base_url}")
        print(f"开始时间: {datetime.now().isoformat()}\n")

        tests = [
            ("历史结算资金费率", self.test_hist_funding_rate),
            ("实时资金费率", self.test_current_funding_rate),
            ("累计资金费率", self.test_accumulated_funding_rate),
            ("交易对资金费率历史", self.test_indicator_funding_rate),
            ("交易对资金费率K线", self.test_kline_funding_rate),
            ("加权资金费率", self.test_weighted_funding_rate),
            ("资金费率热力图", self.test_heatmap_funding_rate),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                print(f"\n测试: {test_name}...")
                result = test_func()
                if result.get("success"):
                    print(f"  ✓ 通过 - 状态码: {result.get('response', {}).status_code}")
                    passed += 1
                else:
                    print(f"  ✗ 失败 - 消息: {result.get('message')}")
                    print(f"     劶态码: {result.get('response', {}).status_code}")
                    print(f"     嶈息: {result.get('response', {}).get('message', 'Unknown error')}")
                    failed += 1
            except Exception as e:
                print(f"  ✗ 异常: {str(e)}")
                failed += 1

                print(f"     异常消息: {str(e)}")

        print("\n" + "=" * 60)
        print(f"测试结果: 通过 {passed}, 失败 {failed}")
        print("=" * 60)

        print(f"通过率: {passed / len(tests) * 100:.1f}%")
        print(f"失败率: {failed / len(tests) * 100:.1f}%")

        return passed == len(tests) and failed == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CoinAnk 资金费率 API 测试")
    parser.add_argument("--url", type=str, default=None, help="服务地址")
    args = parser.parse_args()

    tester = CoinAnkFundingRateTester(args.url) if args.url else tester = CoinAnkFundingRateTester(args.url)

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        tester.close()
