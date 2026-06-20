import os
from common.record_log import logs


def remove_file(filepath, endlst):
    """
    Delete files.
    :param filepath: Path.
    :param endlst: File suffixes to delete, e.g. ['json','txt','attach'].
    :return:
    """
    try:
        if os.path.exists(filepath):
            # Get all file names in the directory.
            dir_lst_files = os.listdir(filepath)
            for file_name in dir_lst_files:
                fpath = os.path.join(filepath,file_name)
                # endswith checks whether a string has the specified suffix.
                if isinstance(endlst, list):
                    for ft in endlst:
                        if file_name.endswith(ft):
                            os.remove(fpath)
                else:
                    raise TypeError('file Type error,must is list')
        else:
            os.makedirs(filepath)
    except Exception as e:
        logs.error(e)


def remove_directory(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logs.error(e)
