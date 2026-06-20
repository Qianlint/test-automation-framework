import logging
import os
import sys

DIR_BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_BASE)

LOG_LEVEL = logging.DEBUG
STREAM_LOG_LEVEL = logging.DEBUG

API_TIMEOUT = 60

SLACK_NOTIFY = True

REPORT_TYPE = 'allure'

FILE_PATH = {
    'CONFIG': os.path.join(DIR_BASE, 'conf/config.ini'),
    'LOG': os.path.join(DIR_BASE, 'logs'),
    'YAML': os.path.join(DIR_BASE),
    'TEMP': os.path.join(DIR_BASE, 'report/temp'),
    'EXTRACT': os.path.join(DIR_BASE, 'extract.yaml'),
    'RESULTXML': os.path.join(DIR_BASE, 'report'),
}

LOGIN_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
}

