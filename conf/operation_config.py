import sys
import traceback
import configparser
from conf import setting
from common.record_log import logs


class OperationConfig:
    """Read and access values from the INI config file."""

    def __init__(self, filepath=None):
        if filepath is None:
            self.__filepath = setting.FILE_PATH['CONFIG']
        else:
            self.__filepath = filepath

        self.conf = configparser.ConfigParser()
        try:
            self.conf.read(self.__filepath, encoding='utf-8')
        except Exception as e:
            exc_type, exc_value, exc_obj = sys.exc_info()
            logs.error(str(traceback.print_exc(exc_obj)))

        self.type = self.get_report_type('type')

    def get_item_value(self, section_name):
        """Return all key-value pairs under a section as a dict."""
        items = self.conf.items(section_name)
        return dict(items)

    def get_section_for_data(self, section, option):
        """Return the value for a given section and option key."""
        try:
            return self.conf.get(section, option)
        except Exception:
            logs.error(str(traceback.format_exc()))
            return ''

    def write_config_data(self, section, option_key, option_value):
        """Write a key-value pair into the INI config file."""
        if section not in self.conf.sections():
            self.conf.add_section(section)
            self.conf.set(section, option_key, option_value)
        else:
            logs.info('Section "%s" already exists, write skipped.' % section)
        with open(self.__filepath, 'w', encoding='utf-8') as f:
            self.conf.write(f)

    def get_section_mysql(self, option):
        return self.get_section_for_data("MYSQL", option)

    def get_report_type(self, option):
        return self.get_section_for_data('REPORT_TYPE', option)
    
    def get_section_mongodb(self, option):
        return self.get_section_for_data("MongoDB", option)
    
    def get_section_redis(self, option):
        return self.get_section_for_data("REDIS", option)
    
    def get_section_ssh(self, option):
        return self.get_section_for_data("SSH", option)