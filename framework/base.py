"""
Base test framework for Market Data Service
Provides common test utilities and reporting
"""
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from framework.api_client import APIClient
from config import REPORT_DIR, VERBOSE


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

    def to_dict(self) -> Dict:
        return {
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "success_rate": round(self.success_rate, 2),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": round(self.duration_seconds, 2),
        }


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

    def _make_result(self, test_name, category, status, message,
                     response_time_ms, error_details=None) -> TestResult:
        """Helper to create and record a test result"""
        result = TestResult(
            test_name=test_name,
            category=category,
            status=status,
            message=message,
            response_time_ms=response_time_ms,
            error_details=error_details,
        )
        self._record_result(result)
        return result

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
        """Generate test report (JSON + HTML)"""
        from framework.reporters.json_reporter import JsonReporter
        from framework.reporters.html_reporter import HtmlReporter

        if not report_name:
            report_name = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        json_reporter = JsonReporter(REPORT_DIR)
        html_reporter = HtmlReporter(REPORT_DIR)

        json_path = json_reporter.generate(report_name, self.summary.to_dict(), self.results)
        html_path = html_reporter.generate(report_name, self.summary.to_dict(), self.results)

        self._log(f"Reports generated: {json_path}, {html_path}")
        return json_path

    def close(self):
        """Close client connection"""
        self.client.close()
