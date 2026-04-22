#!/usr/bin/env python3
"""
Run all tests (V2 + optional V1 legacy)
Usage: python scripts/run_all.py [--include-v1]
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseTester


def main():
    parser = argparse.ArgumentParser(description="Run all tests")
    parser.add_argument("--include-v1", action="store_true",
                        help="Include V1 legacy tests (fund, finance, macro, reference, moneyflow)")
    args = parser.parse_args()

    # Import and run V2 tests
    from scripts.run_v2 import run_modules, DEFAULT_MODULES
    print("Running V2 tests...")
    v2_exit = run_modules(DEFAULT_MODULES)

    exit_code = v2_exit

    if args.include_v1:
        print("\n\n" + "=" * 60)
        print("Running V1 legacy tests...")
        print("=" * 60)

        from tests.v1.test_tushare_fund import test_fund
        from tests.v1.test_tushare_finance import test_finance
        from tests.v1.test_tushare_macro import test_macro
        from tests.v1.test_tushare_reference import test_reference
        from tests.v1.test_tushare_money_flow import test_money_flow

        v1_tester = BaseTester()
        v1_tester.start_test_run()
        try:
            v1_modules = [
                ("Fund", test_fund),
                ("Finance", test_finance),
                ("Macro", test_macro),
                ("Reference", test_reference),
                ("Money Flow", test_money_flow),
            ]
            for name, fn in v1_modules:
                print(f"\n--- V1 Legacy: {name} ---")
                try:
                    fn(v1_tester)
                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")

            v1_tester.end_test_run()
            print(f"\nV1 Legacy Summary: {v1_tester.summary.total_tests} total, "
                  f"{v1_tester.summary.passed} passed, {v1_tester.summary.success_rate:.1f}%")
            v1_tester.generate_report("v1_legacy_test_report")

            if v1_tester.summary.failed > 0:
                exit_code = 1
        finally:
            v1_tester.close()
    else:
        print("\n(Skipping V1 legacy tests. Use --include-v1 to run them)")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
