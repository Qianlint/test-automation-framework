import csv
import hashlib
import os
import random
import time

from common.read_yaml import ReadYamlData
from conf.setting import DIR_BASE


class DebugTalk:

    def __init__(self):
        self.read = ReadYamlData()

    def get_extract_data(self, node_name, index=None):
        """Get extracted value from extract.yaml by key name."""
        return self.read.get_extract_yaml(node_name, index)

    def timestamp(self):
        """Return current Unix timestamp (10 digits)."""
        return int(time.time())

    def md5(self, params):
        """MD5 hash a string."""
        return hashlib.md5(params.encode('utf-8')).hexdigest()

    def read_csv_data(self, file_name, column):
        """Read a column from a CSV file and return a random value."""
        path = os.path.join(DIR_BASE, 'data', file_name)
        with open(path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        return random.choice(rows)[column]