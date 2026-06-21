import time
import json
import re
from json.decoder import JSONDecodeError

import allure
import jsonpath

from common.assertions import Assertions
from common.debug_talk import DebugTalk
from common.read_yaml import get_testcase_yaml, ReadYamlData
from common.record_log import logs
from common.send_request import SendRequest
from conf.operation_config import OperationConfig
from conf.setting import FILE_PATH


class RequestBase:

    def __init__(self):
        self.run = SendRequest()
        self.conf = OperationConfig()
        self.read = ReadYamlData()
        self.asserts = Assertions()

    def replace_load(self, data):
        """Parse and replace YAML data."""
        str_data = data
        if not isinstance(data, str):
            str_data = json.dumps(data, ensure_ascii=False)
            # print('Original data loaded from the YAML file: ', str_data)
        for i in range(str_data.count('${')):
            if '${' in str_data and '}' in str_data:
                start_index = str_data.index('$')
                end_index = str_data.index('}', start_index)
                ref_all_params = str_data[start_index:end_index + 1]
                # Get the function name from the YAML data.
                func_name = ref_all_params[2:ref_all_params.index("(")]
                # Get the function arguments.
                func_params = ref_all_params[ref_all_params.index("(") + 1:ref_all_params.index(")")]
                # Pass the replacement arguments to retrieve the corresponding value via class reflection.
                extract_data = getattr(DebugTalk(), func_name)(*func_params.split(',') if func_params else "")

                if extract_data and isinstance(extract_data, list):
                    extract_data = ','.join(e for e in extract_data)
                str_data = str_data.replace(ref_all_params, str(extract_data))
                # print('Data after parsing and replacement: ', str_data)

        # Restore the original data type.
        if data and isinstance(data, dict):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    def specification_yaml(self, base_info, test_case):
        """
        Base method for processing API requests.
        :param base_info: baseInfo from the YAML file.
        :param test_case: testCase from the YAML file.
        :return:
        """
        try:
            params_type = ['data', 'json', 'params']
            url_host = self.conf.get_section_for_data('api_env', 'host')
            api_name = base_info['api_name']
            allure.attach(api_name, f'API name: {api_name}', allure.attachment_type.TEXT)
            url = url_host + self.replace_load(base_info['url'])
            allure.attach(api_name, f'API URL: {url}', allure.attachment_type.TEXT)
            method = base_info['method']
            allure.attach(api_name, f'Request method: {method}', allure.attachment_type.TEXT)
            header = self.replace_load(base_info['header'])
            if 'header' in test_case:
                header = self.replace_load(test_case.pop('header'))
            allure.attach(api_name, f'Request headers: {header}', allure.attachment_type.TEXT)
            # Process cookies.
            cookie = None
            if base_info.get('cookies') is not None:
                cookie = eval(self.replace_load(base_info['cookies']))
            case_name = test_case.pop('case_name')
            allure.attach(api_name, f'Test case name: {case_name}', allure.attachment_type.TEXT)
            # Process assertions.
            val = self.replace_load(test_case.get('validation'))
            test_case['validation'] = val
            validation = eval(test_case.pop('validation'))
            # Process value extraction.
            extract = test_case.pop('extract', None)
            extract_list = test_case.pop('extract_list', None)
            retry_config = test_case.pop('retry', None)
            max_attempts = retry_config.get('max_attempts', 1) if retry_config else 1
            interval = retry_config.get('interval', 1) if retry_config else 1
            # Process API request parameters.
            for key, value in test_case.items():
                if key in params_type:
                    test_case[key] = self.replace_load(value)

            # Process file-upload APIs.
            file, files = test_case.pop('files', None), None
            if file is not None:
                for fk, fv in file.items():
                    allure.attach(json.dumps(file), 'Uploaded file')
                    files = {fk: open(fv, mode='rb')}

            res = self.run.run_main(name=api_name, url=url, case_name=case_name, header=header, method=method,
                                    file=files, cookies=cookie, **test_case)
            status_code = res.status_code
            allure.attach(self.allure_attach_response(res.json()), 'API response', allure.attachment_type.TEXT)

            for attempt in range(max_attempts):
                res = self.run.run_main(name=api_name, url=url, case_name=case_name, header=header, method=method,
                                        file=files, cookies=cookie, **test_case)
                status_code = res.status_code
                allure.attach(self.allure_attach_response(res.json()), 'API response', allure.attachment_type.TEXT)
                try:
                    res_json = json.loads(res.text)
                    if extract is not None:
                        self.extract_data(extract, res.text)
                    if extract_list is not None:
                        self.extract_data_list(extract_list, res.text)
                    self.asserts.assert_result(validation, res_json, status_code)
                    break
                except JSONDecodeError as js:
                    logs.error('System error or API request was not sent!')
                    raise js
                except Exception as e:
                    if attempt < max_attempts - 1:
                        #logs.info(f'Attempt {attempt + 1}/{max_attempts}: assertion not met yet, retrying in {interval}s...'))
                        time.sleep(interval)
                    else:
                        logs.error(e)
                        raise e

        except Exception as e:
            raise e

    @classmethod
    def allure_attach_response(cls, response):
        if isinstance(response, dict):
            allure_response = json.dumps(response, ensure_ascii=False, indent=4)
        else:
            allure_response = response
        return allure_response

    def extract_data(self, testcase_extarct, response):
        """
        Extract API response values using regular expressions or JSONPath.
        :param testcase_extarct: extract value from the test case YAML file.
        :param response: Actual API response.
        :return:
        """
        try:
            pattern_lst = ['(.*?)', '(.+?)', r'(\d)', r'(\d*)']
            for key, value in testcase_extarct.items():

                # Process regular-expression extraction.
                for pat in pattern_lst:
                    if pat in value:
                        ext_lst = re.search(value, response)
                        if pat in [r'(\d+)', r'(\d*)']:
                            extract_data = {key: int(ext_lst.group(1))}
                        else:
                            extract_data = {key: ext_lst.group(1)}
                        self.read.write_yaml_data(extract_data)
                # Process JSONPath extraction.
                if '$' in value:
                    ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                    if ext_json:
                        extarct_data = {key: ext_json}
                        logs.info('Extracted API response value: ', extarct_data)
                    else:
                        extarct_data = {key: 'No data extracted; check whether the API response is empty!'}
                    self.read.write_yaml_data(extarct_data)
        except Exception as e:
            logs.error(e)

    def extract_data_list(self, testcase_extract_list, response):
        """
        Extract multiple values using regular expressions or JSONPath and return them as a list.
        :param testcase_extract_list: extract_list value from the YAML file.
        :param response: Actual API response. as a string.
        :return:
        """
        try:
            for key, value in testcase_extract_list.items():
                if "(.+?)" in value or "(.*?)" in value:
                    ext_list = re.findall(value, response, re.S)
                    if ext_list:
                        extract_date = {key: ext_list}
                        logs.info('Values extracted by regular expression: %s' % extract_date)
                        self.read.write_yaml_data(extract_date)
                if "$" in value:
                    # Handle empty responses by providing a default value.
                    ext_json = jsonpath.jsonpath(json.loads(response), value)
                    if ext_json:
                        extract_date = {key: ext_json}
                    else:
                        extract_date = {key: "No data extracted; the API response may be empty."}
                    logs.info('Values extracted by JSONPath: %s' % extract_date)
                    self.read.write_yaml_data(extract_date)
        except:
            logs.error('Failed to extract API response values; check the extract_list expression in the YAML file!')


