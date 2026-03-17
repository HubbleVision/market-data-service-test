"""
Glassnode API Test Module
Tests for Glassnode integration endpoints
"""
import time
from typing import Dict, List, Optional
from test_base import BaseTester, TestResult, TestStatus
from api_client import APIClient


class GlassnodeTester(BaseTester):
    """Test Glassnode API endpoints"""

    # Glassnode endpoints to test
    ENDPOINTS = {
        # Market data
        "market_price": {"path": "/api/v1/glassnode/market/price", "params": {"a": "BTC"}},
        "market_marketcap": {"path": "/api/v1/glassnode/market/marketcap", "params": {"a": "BTC"}},
        "market_mvrv": {"path": "/api/v1/glassnode/market/mvrv", "params": {"a": "BTC"}},
        "market_mvrv_z_score": {"path": "/api/v1/glassnode/market/mvrv-z-score", "params": {"a": "BTC"}},
        "market_btc_dominance": {"path": "/api/v1/glassnode/market/btc-dominance", "params": {}},
        "market_realized_marketcap": {"path": "/api/v1/glassnode/market/realized-marketcap", "params": {"a": "BTC"}},
        "market_price_drawdown": {"path": "/api/v1/glassnode/market/price-drawdown", "params": {"a": "BTC"}},
        "market_price_ohlc": {"path": "/api/v1/glassnode/market/price-ohlc", "params": {"a": "BTC"}},

        # Indicators
        "fear_greed": {"path": "/api/v1/glassnode/fear-greed", "params": {}},
        "nupl": {"path": "/api/v1/glassnode/nupl", "params": {"a": "BTC"}},
        "puell_multiple": {"path": "/api/v1/glassnode/puell-multiple", "params": {"a": "BTC"}},
        "sopr": {"path": "/api/v1/glassnode/sopr", "params": {"a": "BTC"}},
        "reserve_risk": {"path": "/api/v1/glassnode/reserve-risk", "params": {"a": "BTC"}},
        "stock_to_flow": {"path": "/api/v1/glassnode/stock-to-flow", "params": {"a": "BTC"}},
        "pi_cycle_top": {"path": "/api/v1/glassnode/pi-cycle-top", "params": {"a": "BTC"}},
        "difficulty_ribbon": {"path": "/api/v1/glassnode/difficulty-ribbon", "params": {"a": "BTC"}},
        "hash_ribbon": {"path": "/api/v1/glassnode/hash-ribbon", "params": {"a": "BTC"}},
        "liveliness": {"path": "/api/v1/glassnode/liveliness", "params": {"a": "BTC"}},
        "cdd": {"path": "/api/v1/glassnode/cdd", "params": {"a": "BTC"}},
        "dormancy": {"path": "/api/v1/glassnode/dormancy", "params": {"a": "BTC"}},
        "velocity": {"path": "/api/v1/glassnode/velocity", "params": {"a": "BTC"}},
        "hodl_waves": {"path": "/api/v1/glassnode/hodl-waves", "params": {"a": "BTC"}},
        "mvrv_by_age": {"path": "/api/v1/glassnode/mvrv-by-age", "params": {"a": "BTC"}},
        "sth_realized_price": {"path": "/api/v1/glassnode/sth-realized-price", "params": {"a": "BTC"}},
        "realized_price": {"path": "/api/v1/glassnode/realized-price", "params": {"a": "BTC"}},
        "realized_profit": {"path": "/api/v1/glassnode/realized-profit", "params": {"a": "BTC"}},
        "realized_loss": {"path": "/api/v1/glassnode/realized-loss", "params": {"a": "BTC"}},
        "net_realized_profit_loss": {"path": "/api/v1/glassnode/net-realized-profit-loss", "params": {"a": "BTC"}},
        "sopr_lth_sth": {"path": "/api/v1/glassnode/sopr-lth-sth", "params": {"a": "BTC"}},

        # Supply
        "supply_current": {"path": "/api/v1/glassnode/supply/current", "params": {"a": "BTC"}},
        "supply_liquid": {"path": "/api/v1/glassnode/supply/liquid", "params": {"a": "BTC"}},
        "supply_illiquid": {"path": "/api/v1/glassnode/supply/illiquid", "params": {"a": "BTC"}},
        "supply_profit": {"path": "/api/v1/glassnode/supply/profit", "params": {"a": "BTC"}},
        "supply_loss": {"path": "/api/v1/glassnode/supply/loss", "params": {"a": "BTC"}},
        "supply_lth": {"path": "/api/v1/glassnode/supply/lth", "params": {"a": "BTC"}},
        "supply_sth": {"path": "/api/v1/glassnode/supply/sth", "params": {"a": "BTC"}},
        "supply_active_24h": {"path": "/api/v1/glassnode/supply/active-24h", "params": {"a": "BTC"}},
        "supply_inflation_rate": {"path": "/api/v1/glassnode/supply/inflation-rate", "params": {"a": "BTC"}},

        # Addresses
        "addresses_non_zero": {"path": "/api/v1/glassnode/addresses/non-zero", "params": {"a": "BTC"}},
        "addresses_active": {"path": "/api/v1/glassnode/addresses/active", "params": {"a": "BTC"}},
        "addresses_count": {"path": "/api/v1/glassnode/addresses/count", "params": {"a": "BTC"}},
        "addresses_sending": {"path": "/api/v1/glassnode/addresses/sending", "params": {"a": "BTC"}},
        "addresses_receiving": {"path": "/api/v1/glassnode/addresses/receiving", "params": {"a": "BTC"}},
        "addresses_profit": {"path": "/api/v1/glassnode/addresses/profit", "params": {"a": "BTC"}},
        "addresses_loss": {"path": "/api/v1/glassnode/addresses/loss", "params": {"a": "BTC"}},
        "addresses_new_non_zero": {"path": "/api/v1/glassnode/addresses/new-non-zero", "params": {"a": "BTC"}},
        "addresses_min_1_btc": {"path": "/api/v1/glassnode/addresses/min-1-btc", "params": {"a": "BTC"}},
        "addresses_min_10_btc": {"path": "/api/v1/glassnode/addresses/min-10-btc", "params": {"a": "BTC"}},

        # Transactions
        "transactions_count": {"path": "/api/v1/glassnode/transactions/count", "params": {"a": "BTC"}},
        "transactions_to_exchanges": {"path": "/api/v1/glassnode/transactions/to-exchanges", "params": {"a": "BTC"}},
        "transactions_from_exchanges": {"path": "/api/v1/glassnode/transactions/from-exchanges", "params": {"a": "BTC"}},
        "transactions_to_exchanges_volume": {"path": "/api/v1/glassnode/transactions/to-exchanges-volume", "params": {"a": "BTC"}},
        "transactions_from_exchanges_volume": {"path": "/api/v1/glassnode/transactions/from-exchanges-volume", "params": {"a": "BTC"}},
        "transactions_transfers_count": {"path": "/api/v1/glassnode/transactions/transfers-count", "params": {"a": "BTC"}},
        "transactions_transfers_volume": {"path": "/api/v1/glassnode/transactions/transfers-volume", "params": {"a": "BTC"}},

        # Mining
        "mining_difficulty": {"path": "/api/v1/glassnode/mining/difficulty", "params": {"a": "BTC"}},
        "mining_hashrate": {"path": "/api/v1/glassnode/mining/hashrate", "params": {"a": "BTC"}},
        "mining_revenue": {"path": "/api/v1/glassnode/mining/revenue", "params": {"a": "BTC"}},
        "mining_thermocap": {"path": "/api/v1/glassnode/mining/thermocap", "params": {"a": "BTC"}},

        # Distribution
        "distribution_exchange_balance": {"path": "/api/v1/glassnode/distribution/exchange-balance", "params": {"a": "BTC"}},
        "distribution_exchange_balance_all": {"path": "/api/v1/glassnode/distribution/exchange-balance-all", "params": {"a": "BTC"}},
        "distribution_exchange_net_position": {"path": "/api/v1/glassnode/distribution/exchange-net-position", "params": {"a": "BTC"}},
        "distribution_gini": {"path": "/api/v1/glassnode/distribution/gini", "params": {"a": "BTC"}},
        "distribution_herfindahl": {"path": "/api/v1/glassnode/distribution/herfindahl", "params": {"a": "BTC"}},

        # Blockchain
        "blockchain_block_height": {"path": "/api/v1/glassnode/blockchain/block-height", "params": {"a": "BTC"}},
        "blockchain_block_size": {"path": "/api/v1/glassnode/blockchain/block-size", "params": {"a": "BTC"}},
        "blockchain_utxo_count": {"path": "/api/v1/glassnode/blockchain/utxo-count", "params": {"a": "BTC"}},

        # Fees
        "fees_volume": {"path": "/api/v1/glassnode/fees/volume", "params": {"a": "BTC"}},
        "fees_volume_mean": {"path": "/api/v1/glassnode/fees/volume-mean", "params": {"a": "BTC"}},

        # ETF
        "etf_balances": {"path": "/api/v1/glassnode/etf-balances", "params": {}},
        "etf_balances_all": {"path": "/api/v1/glassnode/etf-balances-all", "params": {}},
        "etf_flows": {"path": "/api/v1/glassnode/etf-flows", "params": {}},

        # Derivatives
        "derivatives_funding_rate": {"path": "/api/v1/glassnode/derivatives/funding-rate", "params": {"a": "BTC"}},
        "derivatives_futures_oi": {"path": "/api/v1/glassnode/derivatives/futures-oi", "params": {"a": "BTC"}},
        "derivatives_futures_volume": {"path": "/api/v1/glassnode/derivatives/futures-volume", "params": {"a": "BTC"}},
        "derivatives_options_oi": {"path": "/api/v1/glassnode/derivatives/options-oi", "params": {"a": "BTC"}},
        "derivatives_options_volume": {"path": "/api/v1/glassnode/derivatives/options-volume", "params": {"a": "BTC"}},

        # Lightning
        "lightning_capacity": {"path": "/api/v1/glassnode/lightning/capacity", "params": {}},
        "lightning_channels": {"path": "/api/v1/glassnode/lightning/channels", "params": {}},
        "lightning_nodes": {"path": "/api/v1/glassnode/lightning/nodes", "params": {}},

        # Treasuries
        "treasuries_companies": {"path": "/api/v1/glassnode/treasuries/companies", "params": {}},
        "treasuries_governments": {"path": "/api/v1/glassnode/treasuries/governments", "params": {}},

        # DeFi
        "defi_tvl": {"path": "/api/v1/glassnode/defi/tvl", "params": {}},

        # Cost Basis Distribution
        "cost_basis_distribution": {"path": "/api/v1/glassnode/cost-basis-distribution", "params": {"a": "BTC"}},
    }

    def __init__(self, base_url: str = None):
        super().__init__(base_url)

    def test_endpoint(self, name: str, endpoint_config: Dict) -> TestResult:
        """Test a single Glassnode endpoint"""
        start_time = time.time()

        result = TestResult(
            test_name=f"glassnode_{name}",
            category="Glassnode"
        )

        try:
            response = self.client.get(endpoint_config["path"], params=endpoint_config.get("params", {}))
            elapsed_ms = (time.time() - start_time) * 1000
            result.response_time_ms = elapsed_ms

            if response.success:
                data = response.data
                if data:
                    # Glassnode returns data directly or in specific format
                    if isinstance(data, dict):
                        if data.get("success") == False:
                            result.status = TestStatus.FAILED
                            result.message = f"API error: {data.get('detail', 'Unknown')}"
                            result.error_details = str(data)
                        elif "data" in data or "metadata" in data or len(data) > 0:
                            result.status = TestStatus.PASSED
                            result.message = f"Success - {len(str(data))} bytes"
                        else:
                            result.status = TestStatus.PASSED
                            result.message = "Success (empty response)"
                    else:
                        result.status = TestStatus.PASSED
                        result.message = f"Success - {type(data).__name__}"
                elif response.status_code == 204:
                    result.status = TestStatus.PASSED
                    result.message = "Success (No Content)"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "Empty response"
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
        """Run all Glassnode tests"""
        self.start_test_run()

        for name, config in self.ENDPOINTS.items():
            result = self.test_endpoint(name, config)
            self._record_result(result)
            self._log(f"Test {name}: {result.status.value} - {result.message}")

        self.end_test_run()
        return {
            "summary": {
                "total": self.summary.total_tests,
                "passed": self.summary.passed,
                "failed": self.summary.failed,
                "errors": self.summary.errors,
                "success_rate": self.summary.success_rate
            },
            "results": [r.to_dict() for r in self.results]
        }


def run_glassnode_tests():
    """Run Glassnode tests and generate report"""
    tester = GlassnodeTester()
    try:
        results = tester.run_all_tests()
        report_path = tester.generate_report("glassnode_test_report")
        return results, report_path
    finally:
        tester.close()


if __name__ == "__main__":
    results, report_path = run_glassnode_tests()
    print(f"\nReport saved to: {report_path}")
