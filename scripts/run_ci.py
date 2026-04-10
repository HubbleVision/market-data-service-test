#!/usr/bin/env python3
"""
CI test runner (silent output, exit code)
Usage: python scripts/run_ci.py [--skip-v1]
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Suppress verbose logging for CI
os.environ["VERBOSE"] = "false"

from framework import BaseTester
from tests.common.test_health import test_health


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CI test runner")
    parser.add_argument("--skip-v1", action="store_true", default=True,
                        help="Skip V1 legacy tests (default)")
    args = parser.parse_args()

    from scripts.run_v2 import run_modules, DEFAULT_MODULES

    # Run V2 tests silently
    exit_code = run_modules(DEFAULT_MODULES)

    if not args.skip_v1:
        from scripts.run_all import main as run_all_main
        sys.argv = ["run_ci.py", "--include-v1"]
        exit_code = run_all_main()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
