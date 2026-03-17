"""
Test External APIs (CoinAnk + Glassnode)
Run tests for both external API integrations
"""
import argparse
from test_coinank import CoinAnkTester
from test_glassnode import GlassnodeTester


from test_base import TestStatus


import time


import os


import json
from datetime import datetime
from api_client import APIClient
from config import REPORT_DIR, API_KEY, VERBOSE


def run_external_api_tests():
    """Run all external API tests"""
    results = {
        "coinank": None,
        "glassnode": None
    }
    reports = {}

    # Test CoinAnk
    print("\n" + "=" * 60)
    print("Testing CoinAnk API")
    print("=" * 60)
    coinank_tester = CoinAnkTester()
    try:
        results["coinank"] = coinank_tester.run_all_tests()
        reports["coinank"] = coinank_tester.generate_report("coinank_test_report")
        print(f"\nCoinAnk Results: {results['coinank']['summary']['passed']}/{results['coinank']['summary']['total']} passed")
    finally:
        coinank_tester.close()

    # Test Glassnode
    print("\n" + "=" * 60)
    print("Testing Glassnode API")
    print("=" * 60)
    glassnode_tester = GlassnodeTester()
    try:
        results["glassnode"] = glassnode_tester.run_all_tests()
        reports["glassnode"] = glassnode_tester.generate_report("glassnode_test_report")
        print(f"\nGlassnode Results: {results['glassnode']['summary']['passed']}/{results['glassnode']['summary']['total']} passed")
    finally:
        glassnode_tester.close()

    # Generate combined report
    combined_report = {
        "test_time": datetime.now().isoformat(),
        "coinank": results["coinank"]["summary"],
        "glassnode": results["glassnode"]["summary"],
        "coinank_results": results["coinank"]["results"],
        "glassnode_results": results["glassnode"]["results"]
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    combined_path = os.path.join(REPORT_DIR, f"external_apis_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"CoinAnk:  {results['coinank']['summary']['passed']}/{results['coinank']['summary']['total']} passed ({results['coinank']['summary']['success_rate']:.1f}%)")
    print(f"Glassnode: {results['glassnode']['summary']['passed']}/{results['glassnode']['summary']['total']} passed ({results['glassnode']['summary']['success_rate']:.1f}%)")
    print(f"\nCombined report saved to: {combined_path}")

    return results, combined_path


if __name__ == "__main__":
    results, report_path = run_external_api_tests()
