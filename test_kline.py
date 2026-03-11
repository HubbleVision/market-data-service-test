"""
K-Line (Candlestick) Interface Tests
Tests all exchanges' K-line data accessibility and all K-line intervals
"""
from typing import List, Dict
from test_base import BaseTester, TestResult, TestStatus
from api_client import ExchangeType
from config import KLINE_INTERVALS, TEST_SYMBOLS


class KLineTester(BaseTester):
    """Test K-line (candlestick) interfaces for all exchanges"""

    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        self.test_exchanges: List[str] = []
        self.test_symbols: Dict[str, List[str]] = TEST_SYMBOLS
        self.test_intervals: List[str] = KLINE_INTERVALS

    def discover_exchanges(self) -> List[str]:
        """Discover supported exchanges from the service"""
        self._log("Discovering supported exchanges...")

        response = self.client.get_supported_exchanges()
        if response.success and response.data:
            if isinstance(response.data, list):
                self.test_exchanges = response.data
            elif isinstance(response.data, dict) and "exchanges" in response.data:
                self.test_exchanges = response.data["exchanges"]
            self._log(f"Discovered exchanges: {self.test_exchanges}")
        else:
            self._log("Could not discover exchanges, using defaults")
            self.test_exchanges = [e.value for e in ExchangeType]

        return self.test_exchanges

    def test_service_health(self) -> TestResult:
        """Test if the service is healthy and accessible"""
        self._log("Testing service health...")

        response = self.client.health_check()
        result = TestResult(
            test_name="Service Health Check",
            category="infrastructure",
            status=TestStatus.PASSED if response.success else TestStatus.FAILED,
            message="Service is healthy" if response.success else f"Service unhealthy: {response.error}",
            response_time_ms=response.response_time_ms
        )
        self._record_result(result)
        return result

    def test_exchange_kline_access(self, exchange: str, symbol: str = None) -> List[TestResult]:
        """
        Test K-line data accessibility for a specific exchange

        Args:
            exchange: Exchange name
            symbol: Optional specific symbol to test

        Returns:
            List of test results
        """
        results = []

        # Get symbols to test
        symbols = [symbol] if symbol else self.test_symbols.get(exchange, ["BTC/USDT"])

        for sym in symbols:
            self._log(f"Testing K-line access for {exchange} / {sym}")

            response = self.client.get_kline(
                exchange=exchange,
                symbol=sym,
                interval="1h",  # Use common interval
                limit=10
            )

            # Validate response data
            data_valid = False
            if response.success and response.data:
                # Check if data contains expected K-line structure
                if isinstance(response.data, list) and len(response.data) > 0:
                    data_valid = True
                elif isinstance(response.data, dict):
                    # Check for common K-line response structures
                    if "data" in response.data or "klines" in response.data or "candles" in response.data:
                        data_valid = True
                    # Also check for direct kline data with OHLC fields
                    if "open" in response.data or "close" in response.data:
                        data_valid = True

            status = TestStatus.PASSED if response.success and data_valid else TestStatus.FAILED
            message = "K-line data accessible"
            if not response.success:
                message = f"API error: {response.error}"
            elif not data_valid:
                message = "Response received but data structure unexpected"

            result = TestResult(
                test_name=f"K-Line Access: {exchange}",
                category="kline_access",
                exchange=exchange,
                symbol=sym,
                interval="1h",
                status=status,
                message=message,
                response_time_ms=response.response_time_ms,
                error_details=response.error if not response.success else None
            )
            results.append(result)
            self._record_result(result)

        return results

    def test_exchange_interval_access(self, exchange: str, symbol: str = None,
                                       interval: str = None) -> List[TestResult]:
        """
        Test K-line interval accessibility for a specific exchange

        Args:
            exchange: Exchange name
            symbol: Optional specific symbol to test
            interval: Optional specific interval to test

        Returns:
            List of test results
        """
        results = []

        # Get symbols and intervals to test
        symbols = [symbol] if symbol else self.test_symbols.get(exchange, ["BTC/USDT"])
        intervals = [interval] if interval else self.test_intervals

        for sym in symbols:
            for interv in intervals:
                self._log(f"Testing interval {interv} for {exchange} / {sym}")

                response = self.client.get_kline(
                    exchange=exchange,
                    symbol=sym,
                    interval=interv,
                    limit=5
                )

                status = TestStatus.PASSED if response.success else TestStatus.FAILED
                message = f"Interval {interv} accessible" if response.success else f"Failed: {response.error}"

                result = TestResult(
                    test_name=f"K-Line Interval: {exchange}/{interv}",
                    category="kline_interval",
                    exchange=exchange,
                    symbol=sym,
                    interval=interv,
                    status=status,
                    message=message,
                    response_time_ms=response.response_time_ms,
                    error_details=response.error if not response.success else None
                )
                results.append(result)
                self._record_result(result)

        return results

    def test_all_exchanges_kline(self) -> Dict[str, List[TestResult]]:
        """Test K-line access for all exchanges"""
        all_results = {}

        if not self.test_exchanges:
            self.discover_exchanges()

        for exchange in self.test_exchanges:
            self._log(f"\n--- Testing exchange: {exchange} ---")
            all_results[exchange] = self.test_exchange_kline_access(exchange)

        return all_results

    def test_all_intervals(self) -> Dict[str, List[TestResult]]:
        """Test all K-line intervals for all exchanges"""
        all_results = {}

        if not self.test_exchanges:
            self.discover_exchanges()

        for exchange in self.test_exchanges:
            self._log(f"\n--- Testing intervals for exchange: {exchange} ---")
            all_results[exchange] = self.test_exchange_interval_access(exchange)

        return all_results

    def run_all_tests(self) -> Dict:
        """Run all K-line tests and return summary"""
        self.start_test_run()

        # Test 1: Service health
        self.test_service_health()

        # Test 2: Discover exchanges
        self.discover_exchanges()

        # Test 3: Test K-line access for all exchanges
        self._log("\n" + "=" * 40)
        self._log("Phase 1: Testing K-line access for all exchanges")
        self._log("=" * 40)
        self.test_all_exchanges_kline()

        # Test 4: Test all intervals for all exchanges
        self._log("\n" + "=" * 40)
        self._log("Phase 2: Testing all K-line intervals")
        self._log("=" * 40)
        self.test_all_intervals()

        self.end_test_run()

        return {
            "summary": {
                "total": self.summary.total_tests,
                "passed": self.summary.passed,
                "failed": self.summary.failed,
                "success_rate": self.summary.success_rate
            },
            "results": [r.to_dict() for r in self.results]
        }


if __name__ == "__main__":
    tester = KLineTester()
    try:
        tester.run_all_tests()
        tester.generate_report("kline_test")
    finally:
        tester.close()
