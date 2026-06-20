import allure
import pytest
from base.api_util import RequestBase
from base.generate_id import m_id, c_id
from common.read_yaml import get_testcase_yaml

case_login = get_testcase_yaml('./testcase/single_interface/login.yaml')
case_solvers = get_testcase_yaml('./testcase/single_interface/solvers.yaml')
case_submit = get_testcase_yaml('./testcase/single_interface/submit_benchmark.yaml')


@allure.feature(next(m_id) + 'Single Interface Tests')
class TestSingleInterface:

    @allure.story(next(c_id) + 'Login')
    @pytest.mark.parametrize('base_info, test_case', [
        (case_login[0]['baseInfo'], tc) for tc in case_login[0]['testCase']
    ])
    def test_login(self, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)

    @allure.story(next(c_id) + 'List Solvers')
    @pytest.mark.parametrize('base_info, test_case', [
        (case_solvers[0]['baseInfo'], tc) for tc in case_solvers[0]['testCase']
    ])
    def test_solvers(self, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)

    @allure.story(next(c_id) + 'Submit Benchmark')
    @pytest.mark.parametrize('base_info, test_case', [
        (case_submit[0]['baseInfo'], tc) for tc in case_submit[0]['testCase']
    ])
    def test_submit(self, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)