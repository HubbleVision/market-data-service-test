#!/usr/bin/env python3
"""
Complete test runner for all Market Data Service APIs
"""
import sys
import time
sys.path.insert(0, '.')

from test_kline import KLineTester
from test_indicator import IndicatorTester
from test_coinank import CoinAnkTester
from test_glassnode import GlassnodeTester
from test_v2_indicator import V2IndicatorTester


def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_summary(results, name):
    summary = results.get("summary", {})
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    errors = summary.get("errors", 0)
    rate = summary.get("success_rate", 0)
    print(f"\n{name}: {passed}/{total} passed ({rate:.1f}% success)")
    if failed > 0:
        print(f"  - Failed: {failed}")
    if errors > 0:
        print(f"  - Errors: {errors}")


def main():
    print_header("MARKET DATA SERVICE - COMPLETE API TEST")
    print(f"Target: http://localhost:3101")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {}

    # 1. Test K-line APIs
    print_header("1. K-LINE APIs")
    try:
        kline_tester = KLineTester()
        results = kline_tester.run_all_tests()
        kline_tester.generate_report("kline_test")
        all_results["kline"] = results
        print_summary(results, "K-Line")
    except Exception as e:
        print(f"K-Line tests failed: {e}")
        all_results["kline"] = {"summary": {"total": 1, "passed": 0, "failed": 1, "errors": 0, "success_rate": 0}}
    finally:
        kline_tester.close()

    # 2. Test Indicator APIs
    print_header("2. INDICATOR APIs")
    try:
        indicator_tester = IndicatorTester()
        results = indicator_tester.run_all_tests()
        indicator_tester.generate_report("indicator_test")
        all_results["indicator"] = results
        print_summary(results, "Indicators")
    except Exception as e:
        print(f"Indicator tests failed: {e}")
        all_results["indicator"] = {"summary": {"total": 1, "passed": 0, "failed": 1, "errors": 0, "success_rate": 0}}
    finally:
        indicator_tester.close()

    # 3. Test CoinAnk APIs
    print_header("3. COINANK APIs")
    try:
        coinank_tester = CoinAnkTester()
        results = coinank_tester.run_all_tests()
        coinank_tester.generate_report("coinank_test")
        all_results["coinank"] = results
        print_summary(results, "CoinAnk")
    except Exception as e:
        print(f"CoinAnk tests failed: {e}")
        all_results["coinank"] = {"summary": {"total": 1, "passed": 0, "failed": 1, "errors": 0, "success_rate": 0}}
    finally:
        coinank_tester.close()

    # 4. Test Glassnode APIs
    print_header("4. GLASSNODE APIs")
    try:
        glassnode_tester = GlassnodeTester()
        results = glassnode_tester.run_all_tests()
        glassnode_tester.generate_report("glassnode_test")
        all_results["glassnode"] = results
        print_summary(results, "Glassnode")
    except Exception as e:
        print(f"Glassnode tests failed: {e}")
        all_results["glassnode"] = {"summary": {"total": 1, "passed": 0, "failed": 1, "errors": 0, "success_rate": 0}}
    finally:
        glassnode_tester.close()

    # 5. Test V2 Indicator APIs
    print_header("5. V2 INDICATOR APIs")
    try:
        v2_tester = V2IndicatorTester()
        results = v2_tester.run_all_tests()
        v2_tester.generate_report("v2_indicator_test")
        all_results["v2_indicators"] = results
        print_summary(results, "V2 Indicators")
    except Exception as e:
        print(f"V2 Indicator tests failed: {e}")
        all_results["v2_indicators"] = {"summary": {"total": 1, "passed": 0, "failed": 1, "errors": 0, "success_rate": 0}}
    finally:
        v2_tester.close()

    # Overall Summary
    print_header("OVERALL SUMMARY")
    total_all = 0
    passed_all = 0
    failed_all = 0
    errors_all = 0

    for name, results in all_results.items():
        summary = results.get("summary", {})
        total_all += summary.get("total", 0)
        passed_all += summary.get("passed", 0)
        failed_all += summary.get("failed", 0)
        errors_all += summary.get("errors", 0)

    overall_rate = (passed_all / total_all * 100) if total_all > 0 else 0

    print(f"\nTotal Tests: {total_all}")
    print(f"Passed: {passed_all}")
    print(f"Failed: {failed_all}")
    print(f"Errors: {errors_all}")
    print(f"Overall Success Rate: {overall_rate:.1f}%")

    print("\n" + "-" * 70)
    print("Reports saved to ./reports/ directory")
    print("=" * 70)

    return overall_rate >= 80  # Return True if 80%+ tests pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
