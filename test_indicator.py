"""
Technical Indicator Interface Tests
Tests all exchanges' indicator accessibility and computation
"""
from typing import List, Dict
from test_base import BaseTester, TestResult, TestStatus
from api_client import ExchangeType
from config import INDICATORS, TEST_SYMBOLS, KLINE_INTERVALS


# Default parameters for each indicator type
INDICATOR_DEFAULT_PARAMS = {
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


class IndicatorTester(BaseTester):
    """Test technical indicator interfaces for all exchanges"""

    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        self.test_exchanges: List[str] = []
        self.test_symbols: Dict[str, List[str]] = TEST_SYMBOLS
        self.test_indicators: List[str] = INDICATORS
        self.test_intervals: List[str] = KLINE_INTERVALS[:5]  # Use common intervals

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

    def test_indicator_access(self, exchange: str, symbol: str, interval: str,
                               indicator: str, params: List = None) -> TestResult:
        """
        Test a specific indicator for an exchange

        Args:
            exchange: Exchange name
            symbol: Trading pair symbol
            interval: K-line interval
            indicator: Indicator name
            params: Indicator parameters

        Returns:
            Test result
        """
        self._log(f"Testing indicator {indicator} for {exchange} / {symbol} / {interval}")

        # Use default params if not provided
        if params is None:
            params = INDICATOR_DEFAULT_PARAMS.get(indicator, [])

        response = self.client.get_indicator(
            exchange=exchange,
            symbol=symbol,
            interval=interval,
            indicator=indicator,
            params=params
        )

        # Validate response data
        data_valid = False
        if response.success and response.data:
            # Check for expected indicator data structure
            if isinstance(response.data, dict):
                # Common indicator response patterns
                # Check for indicators object containing the computed values
                if "indicators" in response.data:
                    data_valid = True
                # Also check for direct value keys
                expected_keys = [
                    indicator, "value", "values", "data",
                    f"{indicator}_value", "indicator_value",
                    "result", "output"
                ]
                if any(key in response.data for key in expected_keys):
                    data_valid = True
                # Also accept if it contains typical indicator fields
                typical_fields = ["upper", "middle", "lower", "signal", "histogram", "dif", "dea", "macd"]
                if any(field in response.data for field in typical_fields):
                    data_valid = True
            elif isinstance(response.data, list) and len(response.data) > 0:
                data_valid = True

        status = TestStatus.PASSED if response.success and data_valid else TestStatus.FAILED
        message = f"Indicator {indicator} accessible"
        if not response.success:
            message = f"API error: {response.error}"
        elif not data_valid:
            message = "Response received but indicator data structure unexpected"

        result = TestResult(
            test_name=f"Indicator: {exchange}/{indicator}",
            category="indicator_access",
            exchange=exchange,
            symbol=symbol,
            interval=interval,
            indicator=indicator,
            status=status,
            message=message,
            response_time_ms=response.response_time_ms,
            error_details=response.error if not response.success else None
        )
        self._record_result(result)
        return result

    def test_all_indicators_for_exchange(self, exchange: str,
                                          symbol: str = None,
                                          interval: str = "1h") -> List[TestResult]:
        """
        Test all indicators for a specific exchange

        Args:
            exchange: Exchange name
            symbol: Optional specific symbol to test
            interval: K-line interval

        Returns:
            List of test results
        """
        results = []

        # Get symbols to test
        symbols = [symbol] if symbol else self.test_symbols.get(exchange, ["BTC/USDT"])

        for sym in symbols:
            self._log(f"\nTesting all indicators for {exchange} / {sym}")

            for indicator in self.test_indicators:
                # Get default parameters for this indicator
                params = INDICATOR_DEFAULT_PARAMS.get(indicator, [])

                result = self.test_indicator_access(
                    exchange=exchange,
                    symbol=sym,
                    interval=interval,
                    indicator=indicator,
                    params=params
                )
                results.append(result)

        return results

    def test_indicator_across_exchanges(self, indicator: str,
                                         symbol: str = None,
                                         interval: str = "1h") -> Dict[str, TestResult]:
        """
        Test a specific indicator across all exchanges

        Args:
            indicator: Indicator name
            symbol: Optional specific symbol to test
            interval: K-line interval

        Returns:
            Dictionary of exchange -> test result
        """
        results = {}

        if not self.test_exchanges:
            self.discover_exchanges()

        for exchange in self.test_exchanges:
            sym = symbol or self.test_symbols.get(exchange, ["BTC/USDT"])[0]
            params = INDICATOR_DEFAULT_PARAMS.get(indicator, [])

            result = self.test_indicator_access(
                exchange=exchange,
                symbol=sym,
                interval=interval,
                indicator=indicator,
                params=params
            )
            results[exchange] = result

        return results

    def test_all_exchanges_all_indicators(self) -> Dict[str, List[TestResult]]:
        """Test all indicators for all exchanges"""
        all_results = {}

        if not self.test_exchanges:
            self.discover_exchanges()

        for exchange in self.test_exchanges:
            self._log(f"\n--- Testing indicators for exchange: {exchange} ---")
            all_results[exchange] = self.test_all_indicators_for_exchange(exchange)

        return all_results

    def run_all_tests(self) -> Dict:
        """Run all indicator tests and return summary"""
        self.start_test_run()

        # Test 1: Service health
        self.test_service_health()

        # Test 2: Discover exchanges
        self.discover_exchanges()

        # Test 3: Test all indicators for all exchanges
        self._log("\n" + "=" * 40)
        self._log("Testing all indicators for all exchanges")
        self._log("=" * 40)
        self.test_all_exchanges_all_indicators()

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
    tester = IndicatorTester()
    try:
        tester.run_all_tests()
        tester.generate_report("indicator_test")
    finally:
        tester.close()
