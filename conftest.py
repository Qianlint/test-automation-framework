# -*- coding: utf-8 -*-
import time

import pytest

from common.read_yaml import ReadYamlData
from base.remove_file import remove_file
from common.slack_notify import SlackNotify
from conf.setting import SLACK_NOTIFY
from common.record_log import logs
from base.api_util import RequestBase
from common.read_yaml import get_testcase_yaml

import warnings

yfd = ReadYamlData()


@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    # Disable HTTPS and ResourceWarning warnings.
    warnings.simplefilter('ignore', ResourceWarning)

    yfd.clear_yaml_data()
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])

@pytest.fixture(scope='session', autouse=True)
def system_login(clear_extract):
    try:
        api_info = get_testcase_yaml('./testcase/single_interface/login.yaml')
        RequestBase().specification_yaml(api_info[0]['baseInfo'], api_info[0]['testCase'][0])
    except Exception as e:
        logs.error(f'Login failed, cannot continue: {e}')
        exit()


def generate_test_summary(terminalreporter):
    """Generate the test result summary."""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    duration = time.time() - terminalreporter._session_start

    summary = f"""
    Automated test results are shown below. Pay particular attention to failed API tests:
    Total test cases: {total}
    Passed: {passed}
    Failed: {failed}
    Errors: {error}
    Skipped: {skipped}
    Total duration: {duration}
    """
    logs.info(summary)
    return summary


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Collect pytest results automatically and print a summary."""
    summary = generate_test_summary(terminalreporter)
    if SLACK_NOTIFY:
        SlackNotify().send(summary)
