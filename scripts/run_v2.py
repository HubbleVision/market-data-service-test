#!/usr/bin/env python3
"""
Run V2 tests only (daily development)
Usage: python scripts/run_v2.py [--module <module>]
"""
import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _import_func(module_path, func_name):
    """Import a function from a module path (handles numeric directory names)"""
    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)


# Build module registry dynamically
_test_modules = {}

# Common
_test_modules["common"] = [
    ("Health Check", "tests.common.test_health", "test_health"),
]

# Indicators (02_indicators)
_test_modules["indicators"] = [
    ("Validation", "tests.v2.02_indicators.test_validation", "test_validation"),
    ("Single Value", "tests.v2.02_indicators.test_single_value", "test_single_value_indicators"),
    ("Multi Value", "tests.v2.02_indicators.test_multi_value", "test_multi_value_indicators"),
    ("Value Sanity", "tests.v2.02_indicators.test_value_sanity", "test_value_sanity"),
    ("Cross Market", "tests.v2.02_indicators.test_cross_market", "test_cross_market"),
    ("Batch", "tests.v2.02_indicators.test_batch", "test_batch_indicators"),
    ("New Single Value", "tests.v2.02_indicators.test_new_indicators", "test_new_single_value_indicators"),
    ("New Multi Value", "tests.v2.02_indicators.test_new_indicators", "test_new_multi_value_indicators"),
    ("New Custom Params", "tests.v2.02_indicators.test_new_indicators", "test_new_indicators_with_custom_params"),
]

# Crypto (01_crypto)
_test_modules["crypto"] = [
    ("K-line", "tests.v2.01_crypto.test_kline", "test_v2_kline"),
    ("Exchanges", "tests.v2.01_crypto.test_exchanges", "test_v2_exchanges"),
    ("Open Interest", "tests.v2.01_crypto.test_open_interest", "test_open_interest"),
    ("Funding Rate", "tests.v2.01_crypto.test_funding_rate", "test_funding_rate"),
    ("Liquidation", "tests.v2.01_crypto.test_liquidation", "test_liquidation"),
    ("Long/Short", "tests.v2.01_crypto.test_long_short", "test_long_short"),
    ("CVD/BuySell", "tests.v2.01_crypto.test_cvd_buy_sell", "test_cvd_buy_sell"),
    ("ETF", "tests.v2.01_crypto.test_etf", "test_etf"),
    ("Whale/LargeOrder", "tests.v2.01_crypto.test_whale_large_order", "test_whale_large_order"),
    ("Ranking", "tests.v2.01_crypto.test_ranking", "test_ranking"),
    ("OrderBook", "tests.v2.01_crypto.test_orderbook", "test_orderbook"),
    ("Capital Flow", "tests.v2.01_crypto.test_capital_flow", "test_capital_flow"),
    ("Crypto Indicators", "tests.v2.01_crypto.test_crypto_indicators", "test_crypto_indicators"),
    ("Market Overview", "tests.v2.01_crypto.test_market_overview", "test_market_overview"),
    ("News", "tests.v2.01_crypto.test_news", "test_news"),
    ("Crypto Misc", "tests.v2.01_crypto.test_crypto_misc", "test_crypto_misc"),
    ("Crypto Proxy", "tests.v2.01_crypto.test_crypto_proxy", "test_crypto_proxy"),
]

# CNStock (03_cnstock)
_test_modules["cnstock"] = [
    ("Securities", "tests.v2.03_cnstock.test_cn_securities", "test_cnstock_securities"),
    ("Symbols", "tests.v2.03_cnstock.test_symbols", "test_cnstock_symbols"),
    ("Klines", "tests.v2.03_cnstock.test_klines", "test_cnstock_klines"),
    ("Company", "tests.v2.03_cnstock.test_company", "test_cnstock_company"),
    ("Daily Basic", "tests.v2.03_cnstock.test_daily_basic", "test_cnstock_daily_basic"),
    ("Index", "tests.v2.03_cnstock.test_index", "test_cnstock_index"),
    ("Trade Cal", "tests.v2.03_cnstock.test_trade_cal", "test_cnstock_trade_cal"),
    ("Misc", "tests.v2.03_cnstock.test_misc", "test_cnstock_misc"),
    ("Finance", "tests.v2.03_cnstock.test_finance", "test_cnstock_finance"),
    ("Holders", "tests.v2.03_cnstock.test_holders", "test_cnstock_holders"),
    ("MoneyFlow", "tests.v2.03_cnstock.test_moneyflow", "test_cnstock_moneyflow"),
    ("Fund", "tests.v2.03_cnstock.test_fund", "test_cnstock_fund"),
    ("Macro", "tests.v2.03_cnstock.test_macro", "test_cnstock_macro"),
]

# HKStock (04_hkstock)
_test_modules["hkstock"] = [
    ("Securities", "tests.v2.04_hkstock.test_hk_securities", "test_hkstock_securities"),
    ("Symbols", "tests.v2.04_hkstock.test_hk_basic", "test_hkstock_symbols"),
    ("Daily", "tests.v2.04_hkstock.test_hk_basic", "test_hkstock_daily"),
    ("Trade Cal", "tests.v2.04_hkstock.test_hk_basic", "test_hkstock_trade_cal"),
    ("GGT Top10", "tests.v2.04_hkstock.test_hk_connect", "test_hkstock_ggt_top10"),
    ("GGT Daily", "tests.v2.04_hkstock.test_hk_connect", "test_hkstock_ggt_daily"),
    ("Hold", "tests.v2.04_hkstock.test_hk_connect", "test_hkstock_hold"),
    ("Indicators (Single)", "tests.v2.04_hkstock.test_hk_indicators", "test_hkstock_single_value_indicators"),
    ("Indicators (Multi)", "tests.v2.04_hkstock.test_hk_indicators", "test_hkstock_multi_value_indicators"),
]

# USStock (05_usstock)
_test_modules["usstock"] = [
    ("Securities", "tests.v2.05_usstock.test_us_securities", "test_usstock_securities"),
    ("Symbols", "tests.v2.05_usstock.test_us_basic", "test_usstock_symbols"),
    ("Daily", "tests.v2.05_usstock.test_us_basic", "test_usstock_daily"),
    ("Trade Cal", "tests.v2.05_usstock.test_us_basic", "test_usstock_trade_cal"),
    ("Indicators (Single)", "tests.v2.05_usstock.test_us_indicators", "test_usstock_single_value_indicators"),
    ("Indicators (Multi)", "tests.v2.05_usstock.test_us_indicators", "test_usstock_multi_value_indicators"),
    ("AV Backup Securities", "tests.v2.05_usstock.test_usstock_av_backup", "test_usstock_av_securities"),
    ("AV Backup Min", "tests.v2.05_usstock.test_usstock_av_backup", "test_usstock_av_min"),
    ("AV Backup V1 Daily", "tests.v2.05_usstock.test_usstock_av_backup", "test_usstock_av_v1_daily"),
    ("AV Backup V2 Daily", "tests.v2.05_usstock.test_usstock_av_backup", "test_usstock_av_v2_daily"),
]

# Market (06_market)
_test_modules["market"] = [
    ("Quote", "tests.v2.06_market.test_market_quote", "test_market_quote"),
    ("Fuxin Min", "tests.v2.06_market.test_fuxin_min", "test_fuxin_min"),
    ("Fuxin Brokerq", "tests.v2.06_market.test_fuxin_brokerq", "test_fuxin_brokerq"),
    ("Fuxin Orderbook", "tests.v2.06_market.test_fuxin_orderbook", "test_fuxin_orderbook"),
    ("Fuxin Tick", "tests.v2.06_market.test_fuxin_tick", "test_fuxin_tick"),
    ("Symbol Normalize", "tests.v2.06_market.test_symbol_normalize", "test_symbol_normalize"),
    ("Kline AdjFactor", "tests.v2.06_market.test_kline_adj_factor", "test_kline_adj_factor"),
]

# K-line Quality (07_kline_quality)
_test_modules["kline_quality"] = [
    ("OHLC Structure", "tests.v2.07_kline_quality.test_kline_quality", "test_ohlc_structure"),
    ("Price Change", "tests.v2.07_kline_quality.test_kline_quality", "test_price_change"),
    ("Volume Anomaly", "tests.v2.07_kline_quality.test_kline_quality", "test_volume_anomaly"),
    ("Data Freshness", "tests.v2.07_kline_quality.test_kline_quality", "test_data_freshness"),
    ("Cross Verify", "tests.v2.07_kline_quality.test_kline_quality", "test_cross_verify"),
]

# AV Extended (08_av_extended) — Alpha Vantage 新增端点
_test_modules["av_extended"] = [
    ("Search & Status", "tests.v2.08_av_extended.test_av_search_status", "test_av_symbol_search"),
    ("Market Status", "tests.v2.08_av_extended.test_av_search_status", "test_av_market_status"),
    ("Top Gainers/Losers", "tests.v2.08_av_extended.test_av_search_status", "test_av_top_gainers_losers"),
    ("Adjusted Kline (Daily)", "tests.v2.08_av_extended.test_av_adjusted_kline", "test_av_daily_adjusted"),
    ("Adjusted Kline (Weekly)", "tests.v2.08_av_extended.test_av_adjusted_kline", "test_av_weekly_adjusted"),
    ("Adjusted Kline (Monthly)", "tests.v2.08_av_extended.test_av_adjusted_kline", "test_av_monthly_adjusted"),
    ("Income Statement", "tests.v2.08_av_extended.test_av_fundamental", "test_av_income_statement"),
    ("Balance Sheet", "tests.v2.08_av_extended.test_av_fundamental", "test_av_balance_sheet"),
    ("Cash Flow", "tests.v2.08_av_extended.test_av_fundamental", "test_av_cash_flow"),
    ("Earnings Estimates", "tests.v2.08_av_extended.test_av_fundamental", "test_av_earnings_estimates"),
    ("Dividends", "tests.v2.08_av_extended.test_av_fundamental", "test_av_dividends"),
    ("Splits", "tests.v2.08_av_extended.test_av_fundamental", "test_av_splits"),
    ("Shares Outstanding", "tests.v2.08_av_extended.test_av_fundamental", "test_av_shares_outstanding"),
    ("ETF Profile", "tests.v2.08_av_extended.test_av_fundamental", "test_av_etf_profile"),
    ("Listing Status", "tests.v2.08_av_extended.test_av_fundamental", "test_av_listing_status"),
    ("Earnings Calendar", "tests.v2.08_av_extended.test_av_calendar", "test_av_earnings_calendar"),
    ("IPO Calendar", "tests.v2.08_av_extended.test_av_calendar", "test_av_ipo_calendar"),
    ("FX Intraday", "tests.v2.08_av_extended.test_av_fx_extended", "test_av_fx_intraday"),
    ("FX Weekly", "tests.v2.08_av_extended.test_av_fx_extended", "test_av_fx_weekly"),
    ("FX Monthly", "tests.v2.08_av_extended.test_av_fx_extended", "test_av_fx_monthly"),
    ("Crypto Weekly", "tests.v2.08_av_extended.test_av_crypto_extended", "test_av_crypto_weekly"),
    ("Crypto Monthly", "tests.v2.08_av_extended.test_av_crypto_extended", "test_av_crypto_monthly"),
    ("Economic Indicators", "tests.v2.08_av_extended.test_av_economic", "test_av_economic_indicators"),
    # P1: Alpha Intelligence
    ("News Sentiment", "tests.v2.08_av_extended.test_av_intelligence", "test_av_news_sentiment"),
    ("Insider Transactions", "tests.v2.08_av_extended.test_av_intelligence", "test_av_insider_transactions"),
    ("Institutional Holdings", "tests.v2.08_av_extended.test_av_intelligence", "test_av_institutional_holdings"),
    ("Analytics Fixed Window", "tests.v2.08_av_extended.test_av_intelligence", "test_av_analytics_fixed_window"),
    ("Analytics Sliding Window", "tests.v2.08_av_extended.test_av_intelligence", "test_av_analytics_sliding_window"),
    # P1: Commodities
    ("Gold/Silver Spot", "tests.v2.08_av_extended.test_av_commodities", "test_av_gold_silver_spot"),
    ("Gold/Silver History", "tests.v2.08_av_extended.test_av_commodities", "test_av_gold_silver_history"),
    ("Commodity Individual", "tests.v2.08_av_extended.test_av_commodities", "test_av_commodity_individual"),
    ("All Commodities", "tests.v2.08_av_extended.test_av_commodities", "test_av_all_commodities"),
    # P1: Index
    ("Index Data", "tests.v2.08_av_extended.test_av_index", "test_av_index_data"),
    ("Index Catalog", "tests.v2.08_av_extended.test_av_index", "test_av_index_catalog"),
]

DEFAULT_MODULES = ["common", "indicators", "crypto", "cnstock", "hkstock", "usstock", "market", "kline_quality", "av_extended"]


def run_modules(selected_modules):
    from framework import BaseTester

    tester = BaseTester()
    tester.start_test_run()

    try:
        for mod_name in selected_modules:
            if mod_name not in _test_modules:
                print(f"[WARN] Unknown module: {mod_name}, skipping")
                continue

            tests = _test_modules[mod_name]
            print(f"\n{'=' * 50}")
            print(f"Module: {mod_name} ({len(tests)} test groups)")
            print(f"{'=' * 50}")

            for name, mod_path, func_name in tests:
                print(f"\n--- {name} ---")
                try:
                    fn = _import_func(mod_path, func_name)
                    fn(tester)
                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")

        tester.end_test_run()

        print(f"\n{'=' * 60}")
        print(f"V2 Test Summary")
        print(f"{'=' * 60}")
        print(f"Total: {tester.summary.total_tests}")
        print(f"Passed: {tester.summary.passed}")
        print(f"Failed: {tester.summary.failed}")
        print(f"Skipped: {tester.summary.skipped}")
        print(f"Errors: {tester.summary.errors}")
        print(f"Success rate: {tester.summary.success_rate:.1f}%")

        tester.generate_report("v2_test_report")

        return 0 if tester.summary.failed == 0 else 1
    finally:
        tester.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run V2 tests")
    parser.add_argument("--module", "-m", type=str, default=None,
                        help="Module to run: common, indicators, crypto, cnstock, hkstock, usstock")
    args = parser.parse_args()

    modules = [args.module] if args.module else DEFAULT_MODULES
    sys.exit(run_modules(modules))


if __name__ == "__main__":
    main()
