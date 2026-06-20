import pandas as pd
from common.record_log import logs
import traceback


def read_csv(filepath, col_name):
    """
    :param filepath: CSV path.
    :param col_name: Column name to read.
    usecols: Columns to read, specified by position or name.
    error_bad_lines = False skips malformed rows without raising an error.
    :return:
    """
    try:
        df = pd.read_csv(filepath, encoding="GBK")
        data = df[col_name].tolist()
        return data
    except Exception:
        logs.error(str(traceback.format_exc()))
