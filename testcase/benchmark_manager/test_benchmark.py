import allure
import pytest
from base.api_util import RequestBase
from base.generate_id import m_id, c_id
from common.read_yaml import get_testcase_yaml

case_flow = get_testcase_yaml('./testcase/benchmark_manager/full_flow.yaml')


@allure.feature(next(m_id) + 'Benchmark Manager')
class TestBenchmarkManager:

    @allure.story(next(c_id) + 'Full Benchmark Flow')
    @pytest.mark.parametrize('base_info, test_case', [
        (case['baseInfo'], tc)
        for case in case_flow
        for tc in case['testCase']
    ])
    def test_full_flow(self, system_login, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)