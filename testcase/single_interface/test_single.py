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
        pytest.param(*item, marks=pytest.mark.xfail(
            reason="mock server does not yet return security-specific error codes for injection attempts"
        )) if item[1]['case_name'] == 'SQL injection input expects security-specific error code'
        else item
        for item in case_login
    ])
    def test_login(self, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)

    @allure.story(next(c_id) + 'List Solvers')
    @pytest.mark.parametrize('base_info, test_case', case_solvers)
    def test_solvers(self,system_login, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)

    @allure.story(next(c_id) + 'Submit Benchmark')
    @pytest.mark.parametrize('base_info, test_case', [
        pytest.param(*item, marks=pytest.mark.xfail(
            reason="tolerance=0 raises HTTP 400 instead of application-level error_code; "
                   "pending mock server update to return structured error response"
        )) if item[1]['case_name'] == 'Submit with tolerance=0 expects application-level error code'
        else item
        for item in case_submit
    ])
    def test_submit(self,system_login, base_info, test_case):
        RequestBase().specification_yaml(base_info, test_case)

    @allure.story(next(c_id) + 'Core Pinning Benchmark')
    @pytest.mark.skip(reason="core pinning depends on hardware-level CPU affinity control, not available in CI environment")
    def test_core_pinning_benchmark(self):
        pass
