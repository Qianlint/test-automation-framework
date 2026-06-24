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
    """Load and package test case data from a YAML file.
    Single-group files return [[baseInfo, tc], ...] ready for parametrize.
    Multi-group files return raw data.
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if len(data) == 1:
            base_info = data[0].get('baseInfo')
            return [[base_info, tc] for tc in data[0].get('testCase', [])]
        return data
    except FileNotFoundError:
        logs.error(f'[{file_path}] file not found, check the path')
    except UnicodeDecodeError:
        logs.error(f'[{file_path}] encoding error, ensure the file is UTF-8')
    except Exception as e:
        logs.error(f'Error loading [{file_path}]: {str(e)}')