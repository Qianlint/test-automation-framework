import traceback
import allure
import jsonpath
import operator

from common.record_log import logs
from common.connection import ConnectMysql


class Assertions:
    """"
    Supported API assertion modes:
    1) Response text contains the expected string
    2) Response result equals the expected result
    3) Response result does not equal the expected result
    4) Any response value equals the expected value
    5) Database assertion

    """

    def contains_assert(self, value, response, status_code):
        """
        Assert that the expected string is contained in the API response.
        :param value: Expected result value from the YAML file
        :param response: Actual API response
        :param status_code: Response status code
        :return: Result status flag
        """
        # Assertion status flag: 0 indicates success; any other value indicates failure
        flag = 0
        for assert_key, assert_value in value.items():
            if assert_key == "status_code":
                if assert_value != status_code:
                    flag += 1
                    allure.attach(f"Expected result: {assert_value}\nActual result: {status_code}", 'Response status code assertion: failed',
                                  attachment_type=allure.attachment_type.TEXT)
                    logs.error("Contains assertion failed: response status code [%s] does not equal [%s]" % (status_code, assert_value))
            else:
                resp_list = jsonpath.jsonpath(response, "$..%s" % assert_key)
                if isinstance(resp_list[0], str):
                    resp_list = ''.join(resp_list)
                if resp_list:
                    assert_value = None if assert_value.upper() == 'NONE' else assert_value
                    if assert_value in resp_list:
                        logs.info("String contains assertion passed: expected [%s], actual [%s]" % (assert_value, resp_list))
                    else:
                        flag = flag + 1
                        allure.attach(f"Expected result: {assert_value}\nActual result: {resp_list}", 'Response text assertion: failed',
                                      attachment_type=allure.attachment_type.TEXT)
                        logs.error("Response text assertion failed: expected [%s], actual [%s]" % (assert_value, resp_list))
        return flag

    def equal_assert(self, expected_results, actual_results, statuc_code=None):
        """
        Equality assertion mode.
        :param expected_results: Expected validation value from the YAML file
        :param actual_results: Actual API response
        :return:
        """
        flag = 0
        if isinstance(actual_results, dict) and isinstance(expected_results, dict):
            # Find the key shared by the actual and expected results
            common_keys = list(expected_results.keys() & actual_results.keys())[0]
            # Build a new actual-result dictionary using the shared key
            new_actual_results = {common_keys: actual_results[common_keys]}
            eq_assert = operator.eq(new_actual_results, expected_results)
            if eq_assert:
                logs.info(f"Equality assertion passed: actual result {new_actual_results} equals expected result: " + str(expected_results))
                allure.attach(f"Expected result: {str(expected_results)}\nActual result: {new_actual_results}", 'Equality assertion: passed',
                              attachment_type=allure.attachment_type.TEXT)
            else:
                flag += 1
                logs.error(f"Equality assertion failed: actual result {new_actual_results} does not equal expected result: " + str(expected_results))
                allure.attach(f"Expected result: {str(expected_results)}\nActual result: {new_actual_results}", 'Equality assertion: failed',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('Equality assertion type error: expected and actual results must be dictionaries!')
        return flag

    def not_equal_assert(self, expected_results, actual_results, statuc_code=None):
        """
        Inequality assertion mode.
        :param expected_results: Expected validation value from the YAML file
        :param actual_results: Actual API response
        :return:
        """
        flag = 0
        if isinstance(actual_results, dict) and isinstance(expected_results, dict):
            # Find the key shared by the actual and expected results
            common_keys = list(expected_results.keys() & actual_results.keys())[0]
            # Build a new actual-result dictionary using the shared key
            new_actual_results = {common_keys: actual_results[common_keys]}
            eq_assert = operator.ne(new_actual_results, expected_results)
            if eq_assert:
                logs.info(f"Inequality assertion passed: actual result {new_actual_results} does not equal expected result: " + str(expected_results))
                allure.attach(f"Expected result: {str(expected_results)}\nActual result: {new_actual_results}", 'Inequality assertion: passed',
                              attachment_type=allure.attachment_type.TEXT)
            else:
                flag += 1
                logs.error(f"Inequality assertion failed: actual result {new_actual_results} equals expected result: " + str(expected_results))
                allure.attach(f"Expected result: {str(expected_results)}\nActual result: {new_actual_results}", 'Inequality assertion: failed',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('Inequality assertion type error: expected and actual results must be dictionaries!')
        return flag

    def assert_response_any(self, actual_results, expected_results):
        """
        Assert any property value in the API response body.
        :param actual_results: Actual API response
        :param expected_results: Expected value from anywhere in the API response
        :return: Status flag; 0 indicates success and any nonzero value indicates failure
        """
        flag = 0
        try:
            exp_key = list(expected_results.keys())[0]
            if exp_key in actual_results:
                act_value = actual_results[exp_key]
                rv_assert = operator.eq(act_value, list(expected_results.values())[0])
                if rv_assert:
                    logs.info("Any response value assertion passed")
                else:
                    flag += 1
                    logs.error("Any response value assertion failed")
        except Exception as e:
            logs.error(e)
            raise
        return flag

    def assert_response_time(self, res_time, exp_time):
        """
        Assert that the API response time is less than the expected response time.
        :param res_time: Actual API response time
        :param exp_time: Expected response time
        :return:
        """
        try:
            assert res_time < exp_time
            return True
        except Exception as e:
            logs.error('API response time [%ss] exceeds the expected time [%ss]' % (res_time, exp_time))
            raise

    def assert_mysql_data(self, expected_results):
        """
        Database assertion.
        :param expected_results: SQL statement from the YAML file
        :return: Status flag; 0 indicates success and any nonzero value indicates failure
        """
        flag = 0
        conn = ConnectMysql()
        db_value = conn.query_all(expected_results)
        if db_value is not None:
            logs.info("Database assertion passed")
        else:
            flag += 1
            logs.error("Database assertion failed; verify that the data exists in the database!")
        return flag

    def assert_result(self, expected, response, status_code):
        """
        Run assertions using all_flag; all_flag == 0 indicates success, otherwise failure.
        :param expected: Expected result
        :param response: Actual response
        :param status_code: Response status code
        :return:
        """
        all_flag = 0
        try:
            logs.info("Expected result from YAML file: %s" % expected)
            # logs.info("Actual result: %s" % response)
            # all_flag = 0
            for yq in expected:
                for key, value in yq.items():
                    if key == "contains":
                        flag = self.contains_assert(value, response, status_code)
                        all_flag = all_flag + flag
                    elif key == "eq":
                        flag = self.equal_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'ne':
                        flag = self.not_equal_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'rv':
                        flag = self.assert_response_any(actual_results=response, expected_results=value)
                        all_flag = all_flag + flag
                    elif key == 'db':
                        flag = self.assert_mysql_data(value)
                        all_flag = all_flag + flag
                    else:
                        logs.error("Unsupported assertion mode")

        except Exception as exceptions:
            logs.error('API assertion error; verify that the expected result in the YAML file is correct!')
            raise exceptions

        if all_flag == 0:
            logs.info("Test passed")
            assert True
        else:
            logs.error("Test failed")
            assert False
