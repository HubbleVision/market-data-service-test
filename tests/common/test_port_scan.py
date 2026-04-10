"""
Port scan test to find running services
"""
import socket
from framework import BaseTester, TestResult, TestStatus


def test_port_scan(tester: BaseTester) -> list:
    """Scan common ports for running services"""
    results = []

    ports = [3000, 3101, 5000, 8000, 8080, 9000, 9090]
    host = tester.client.base_url.split("//")[1].split(":")[0] or "localhost"

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result_code = sock.connect_ex((host, port))
        sock.close()

        is_open = result_code == 0
        results.append(tester._make_result(
            f"Port {port}",
            "common",
            TestStatus.PASSED if is_open else TestStatus.SKIPPED,
            f"port {port} - {'open' if is_open else 'closed'}",
            0,
            None,
        ))

    return results
