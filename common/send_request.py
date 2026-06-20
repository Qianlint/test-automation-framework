import requests
from common.record_log import logs
from conf.setting import API_TIMEOUT


class SendRequest:

    def __init__(self):
        self.session = requests.Session()

    def run_main(self, name, url, case_name, header, method, file=None, cookies=None, **kwargs):
        logs.info(f'Test case: {case_name} | API: {name} | URL: {url}')
        response = self.session.request(
            method=method,
            url=url,
            headers=header,
            files=file,
            cookies=cookies,
            timeout=API_TIMEOUT,
            **kwargs
        )
        logs.info(f'Status code: {response.status_code}')
        return response