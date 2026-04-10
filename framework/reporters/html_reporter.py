"""HTML report generator"""
import os
from typing import Dict, List
from framework.base import TestResult


class HtmlReporter:
    """Generate HTML test reports"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate(self, report_name: str, summary: dict, results: List[TestResult]) -> str:
        os.makedirs(self.output_dir, exist_ok=True)

        status_colors = {
            "passed": "#4CAF50",
            "failed": "#f44336",
            "skipped": "#FF9800",
            "error": "#9C27B0",
            "pending": "#9E9E9E"
        }

        rows = ""
        for r in results:
            color = status_colors.get(r.status.value, "#9E9E9E")
            rows += f"""
                <tr>
                    <td>{r.test_name}</td>
                    <td>{r.category}</td>
                    <td>{r.exchange or '-'}</td>
                    <td>{r.symbol or '-'}</td>
                    <td>{r.interval or '-'}</td>
                    <td style="background-color: {color}; color: white;">{r.status.value.upper()}</td>
                    <td>{r.response_time_ms:.0f}ms</td>
                    <td>{r.message}</td>
                </tr>
            """

        html = f"""
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

        path = os.path.join(self.output_dir, f"{report_name}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        return path
