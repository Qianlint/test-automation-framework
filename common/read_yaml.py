import yaml
from conf.setting import FILE_PATH
from common.record_log import logs


class ReadYamlData:

    def get_extract_yaml(self, node_name, index=None):
        """Read a value from extract.yaml by key name."""
        with open(FILE_PATH['EXTRACT'], encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        value = data.get(node_name)
        if isinstance(value, list) and index is not None:
            return value[int(index)]
        return value

    def write_yaml_data(self, data: dict):
        """Write extracted values to extract.yaml."""
        try:
            with open(FILE_PATH['EXTRACT'], encoding='utf-8') as f:
                existing = yaml.safe_load(f) or {}
        except FileNotFoundError:
            existing = {}
        existing.update(data)
        with open(FILE_PATH['EXTRACT'], 'w', encoding='utf-8') as f:
            yaml.dump(existing, f, allow_unicode=True)
        logs.info(f'Extracted data saved: {data}')

    def clear_yaml_data(self):
        """Clear extract.yaml before each test run."""
        with open(FILE_PATH['EXTRACT'], 'w', encoding='utf-8') as f:
            yaml.dump({}, f)


def get_testcase_yaml(file_path):
    """Load test case data from a YAML file."""
    with open(file_path, encoding='utf-8') as f:
        return yaml.safe_load(f)