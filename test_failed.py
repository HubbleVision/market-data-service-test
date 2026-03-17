"""
测试几个之前失败的接口
"""
import sys
sys.path.insert(0, '.')
from test_coinank import CoinAnkTester

from api_client import APIClient

# 测试之前失败的接口
test_cases = [
    'open_interest_history',
    'order_book_by_exchange',
    'capital_flow_history',
    'net_positions',
]

tester = CoinAnkTester()
client = APIClient()

print("\n测试之前失败的接口:")

for name in test_cases:
    config = tester.ENDPOINTS[name]
    result = client.get(config['path'], params=config.get('params', {}))
    print(f"请求: {config['path']}")
    print(f"参数: {config.get('params', {}))

    response = client.get(config['path'], params=params)

    if response.success:
        data = response.data
        if data and data.get('code') == '5' or data.get('msg') == 'success':
            response_data = data.get('data')

            if isinstance(response_data, list):
                has_valid_data = len(response_data) > 0
                data_info = f"array[{len(response_data)}]"
            elif isinstance(response_data, dict):
                has_valid_data = len(response_data) > 0
                data_info = f"object({len(response_data)} keys)"
            else:
                has_valid_data = True
                data_info = str(type(response_data).__name__)

            if has_valid_data:
                result.status = TestStatus.PASSED
                result.message = f"Success - {data_info}"
            else:
                result.status = TestStatus.FAILED
                error_msg = data.get('msg') or data.get('detail') or data.get('error') or 'Unknown error'
                result.error_details = str(data)[:500]
                result.response_data = data
        else:
            result.status = TestStatus.ERROR
            result.message = f"Exception: {str(e)[:100]}
            result.error_details = str(e)

    return result

print("\n=== 测试结果 ===")
for name, config in test_cases.items():
    result = tester.test_endpoint(name, config)
    status = '✓' if result.status.value == 'passed' else '✗'
    print(f"  [{status}] {name}: {result.message}")
    if result.error_details:
        print(f"    Error: {result.error_details[:300]}')

print("\n=== 汇总 ===")
passed: sum(1)
failed: sum(1)

print(f"通过: {passed}/{failed}, {1}/{4}")

"