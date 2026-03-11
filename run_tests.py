#!/usr/bin/env python3
"""
Simple test runner to verify market data service
"""
import sys
sys.path.insert(0, '.')

from test_kline import KLineTester
from test_indicator import IndicatorTester

def main():
    print("=" * 60)
    print("MARKET DATA SERVICE TEST")
    print("=" * 60)

    # Test K-line
    print("\n--- Testing K-line interfaces ---")
    kline_tester = KLineTester()
    try:
        kline_tester.run_all_tests()
        kline_tester.generate_report("kline_test")
    finally:
        kline_tester.close()

    # Test Indicators
    print("\n--- Testing Indicator interfaces ---")
    indicator_tester = IndicatorTester()
    try:
        indicator_tester.run_all_tests()
        indicator_tester.generate_report("indicator_test")
    finally:
        indicator_tester.close()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"K-line: {kline_tester.summary.passed}/{kline_tester.summary.total_tests} passed")
    print(f"Indicators: {indicator_tester.summary.passed}/{indicator_tester.summary.total_tests} passed")

if __name__ == "__main__":
    main()
