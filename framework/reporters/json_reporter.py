"""JSON report generator"""
import json
import os
from typing import Dict, List
from framework.base import TestResult


class JsonReporter:
    """Generate JSON test reports"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate(self, report_name: str, summary: dict, results: List[TestResult]) -> str:
        os.makedirs(self.output_dir, exist_ok=True)

        report = {
            "summary": summary,
            "results": [r.to_dict() for r in results]
        }

        path = os.path.join(self.output_dir, f"{report_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return path
