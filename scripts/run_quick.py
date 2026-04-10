#!/usr/bin/env python3
"""
Quick smoke test (seconds)
Usage: python scripts/run_quick.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseTester
from tests.common.test_health import test_health


def main():
    tester = BaseTester()
    tester.start_test_run()

    try:
        print("Running quick smoke test...")
        test_health(tester)
        tester.end_test_run()

        status = "OK" if tester.summary.failed == 0 else "FAILED"
        print(f"\nSmoke test: {status} ({tester.summary.passed}/{tester.summary.total_tests} passed)")

        sys.exit(0 if tester.summary.failed == 0 else 1)
    finally:
        tester.close()


if __name__ == "__main__":
    main()
