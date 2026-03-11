#!/usr/bin/env python3
"""
Market Data Service Test Suite
Main entry point for running all tests
"""
import argparse
import sys
from datetime import datetime

from config import BASE_URL, REPORT_DIR, VERBOSE
from test_kline import KLineTester
from test_indicator import IndicatorTester


def run_kline_tests(base_url: str = None, output_prefix: str = None):
    """Run K-line tests"""
    print("\n" + "=" * 60)
    print("K-LINE INTERFACE TESTS")
    print("=" * 60)

    tester = KLineTester(base_url)
    try:
        tester.run_all_tests()
        report_name = output_prefix or f"kline_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tester.generate_report(report_name)
        return tester.summary.failed == 0
    finally:
        tester.close()


def run_indicator_tests(base_url: str = None, output_prefix: str = None):
    """Run indicator tests"""
    print("\n" + "=" * 60)
    print("INDICATOR INTERFACE TESTS")
    print("=" * 60)

    tester = IndicatorTester(base_url)
    try:
        tester.run_all_tests()
        report_name = output_prefix or f"indicator_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tester.generate_report(report_name)
        return tester.summary.failed == 0
    finally:
        tester.close()


def run_all_tests(base_url: str = None, output_prefix: str = None):
    """Run all test suites"""
    print("\n" + "=" * 60)
    print("MARKET DATA SERVICE - FULL TEST SUITE")
    print("=" * 60)
    print(f"Service URL: {base_url or BASE_URL}")
    print(f"Report Directory: {REPORT_DIR}")
    print(f"Started at: {datetime.now().isoformat()}")

    results = {
        "kline": False,
        "indicator": False
    }

    # Run K-line tests
    results["kline"] = run_kline_tests(base_url, f"{output_prefix}_kline" if output_prefix else None)

    # Run indicator tests
    results["indicator"] = run_indicator_tests(base_url, f"{output_prefix}_indicator" if output_prefix else None)

    # Print summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)
    print(f"K-line tests: {'PASSED' if results['kline'] else 'FAILED'}")
    print(f"Indicator tests: {'PASSED' if results['indicator'] else 'FAILED'}")

    all_passed = all(results.values())
    print(f"\nOverall result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 60)

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Market Data Service Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run all tests
  python main.py --kline            # Run only K-line tests
  python main.py --indicator        # Run only indicator tests
  python main.py --url http://localhost:8080  # Use custom service URL
  python main.py --output my_test   # Custom output filename prefix
        """
    )

    parser.add_argument(
        "--kline",
        action="store_true",
        help="Run only K-line interface tests"
    )
    parser.add_argument(
        "--indicator",
        action="store_true",
        help="Run only indicator interface tests"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help=f"Base URL for the market data service (default: {BASE_URL})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output filename prefix for reports"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Handle verbose flag
    if args.verbose:
        import config
        config.VERBOSE = True

    # Determine which tests to run
    run_kline = args.kline
    run_indicator = args.indicator
    run_all = not (run_kline or run_indicator)

    success = True

    if run_all:
        success = run_all_tests(args.url, args.output)
    else:
        if run_kline:
            success = run_kline_tests(args.url, args.output) and success
        if run_indicator:
            success = run_indicator_tests(args.url, args.output) and success

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
