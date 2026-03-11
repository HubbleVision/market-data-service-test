"""
Base test framework for Market Data Service
Provides common test utilities and reporting
"""
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from api_client import APIClient
from config import REPORT_DIR, VERBOSE, KLINE_INTERVALS, INDICATORS, TEST_SYMBOLS


class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    category: str
    exchange: Optional[str] = None
    symbol: Optional[str] = None
    interval: Optional[str] = None
    indicator: Optional[str] = None
    status: TestStatus = TestStatus.PENDING
    message: str = ""
    response_time_ms: float = 0.0
    error_details: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass
class TestSummary:
    """Summary of test run"""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    duration_seconds: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100


class BaseTester:
    """Base class for all testers"""

    def __init__(self, base_url: str = None):
        self.client = APIClient(base_url) if base_url else APIClient()
        self.results: List[TestResult] = []
        self.summary = TestSummary()
        self._start_time = None

    def _log(self, message: str, level: str = "INFO"):
        """Log message"""
        if VERBOSE:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def _record_result(self, result: TestResult):
        """Record test result"""
        self.results.append(result)
        self.summary.total_tests += 1

        if result.status == TestStatus.PASSED:
            self.summary.passed += 1
        elif result.status == TestStatus.FAILED:
            self.summary.failed += 1
        elif result.status == TestStatus.SKIPPED:
            self.summary.skipped += 1
        elif result.status == TestStatus.ERROR:
            self.summary.errors += 1

    def start_test_run(self):
        """Start test run"""
        self._start_time = time.time()
        self._log("=" * 60)
        self._log("Starting test run")
        self._log("=" * 60)

    def end_test_run(self):
        """End test run"""
        self.summary.end_time = datetime.now().isoformat()
        if self._start_time:
            self.summary.duration_seconds = time.time() - self._start_time
        self._log("=" * 60)
        self._log(f"Test run completed in {self.summary.duration_seconds:.2f}s")
        self._log(f"Total: {self.summary.total_tests}, "
                  f"Passed: {self.summary.passed}, "
                  f"Failed: {self.summary.failed}, "
                  f"Skipped: {self.summary.skipped}, "
                  f"Errors: {self.summary.errors}")
        self._log(f"Success rate: {self.summary.success_rate:.1f}%")
        self._log("=" * 60)

    def generate_report(self, report_name: str = None) -> str:
        """Generate test report"""
        os.makedirs(REPORT_DIR, exist_ok=True)

        if not report_name:
            report_name = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        report = {
            "summary": {
                "total_tests": self.summary.total_tests,
                "passed": self.summary.passed,
                "failed": self.summary.failed,
                "skipped": self.summary.skipped,
                "errors": self.summary.errors,
                "success_rate": round(self.summary.success_rate, 2),
                "start_time": self.summary.start_time,
                "end_time": self.summary.end_time,
                "duration_seconds": round(self.summary.duration_seconds, 2)
            },
            "results": [r.to_dict() for r in self.results]
        }

        # JSON report
        json_path = os.path.join(REPORT_DIR, f"{report_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # HTML report
        html_path = os.path.join(REPORT_DIR, f"{report_name}.html")
        html_content = self._generate_html_report(report)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self._log(f"Reports generated: {json_path}, {html_path}")
        return json_path

    def _generate_html_report(self, report: Dict) -> str:
        """Generate HTML report"""
        summary = report["summary"]
        results = report["results"]

        status_colors = {
            "passed": "#4CAF50",
            "failed": "#f44336",
            "skipped": "#FF9800",
            "error": "#9C27B0",
            "pending": "#9E9E9E"
        }

        rows = ""
        for r in results:
            color = status_colors.get(r["status"], "#9E9E9E")
            rows += f"""
                <tr>
                    <td>{r['test_name']}</td>
                    <td>{r['category']}</td>
                    <td>{r['exchange'] or '-'}</td>
                    <td>{r['symbol'] or '-'}</td>
                    <td>{r['interval'] or '-'}</td>
                    <td style="background-color: {color}; color: white;">{r['status'].upper()}</td>
                    <td>{r['response_time_ms']:.0f}ms</td>
                    <td>{r['message']}</td>
                </tr>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Market Data Service Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 15px; margin: 20px 0; }}
        .summary-card {{ background: #f9f9f9; padding: 15px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #666; font-size: 14px; }}
        .summary-card .value {{ font-size: 28px; font-weight: bold; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #2196F3; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .pass {{ color: #4CAF50; font-weight: bold; }}
        .fail {{ color: #f44336; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Market Data Service Test Report</h1>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">{summary['total_tests']}</div>
            </div>
            <div class="summary-card" style="border-left: 4px solid #4CAF50;">
                <h3>Passed</h3>
                <div class="value pass">{summary['passed']}</div>
            </div>
            <div class="summary-card" style="border-left: 4px solid #f44336;">
                <h3>Failed</h3>
                <div class="value fail">{summary['failed']}</div>
            </div>
            <div class="summary-card" style="border-left: 4px solid #FF9800;">
                <h3>Skipped</h3>
                <div class="value">{summary['skipped']}</div>
            </div>
            <div class="summary-card" style="border-left: 4px solid #9C27B0;">
                <h3>Errors</h3>
                <div class="value">{summary['errors']}</div>
            </div>
            <div class="summary-card" style="border-left: 4px solid #2196F3;">
                <h3>Success Rate</h3>
                <div class="value">{summary['success_rate']}%</div>
            </div>
        </div>

        <p><strong>Start Time:</strong> {summary['start_time']} |
           <strong>End Time:</strong> {summary['end_time']} |
           <strong>Duration:</strong> {summary['duration_seconds']}s</p>

        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Category</th>
                    <th>Exchange</th>
                    <th>Symbol</th>
                    <th>Interval</th>
                    <th>Status</th>
                    <th>Response Time</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>
        """

    def close(self):
        """Close client connection"""
        self.client.close()
