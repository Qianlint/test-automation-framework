import logging
import os
from conf.setting import FILE_PATH, LOG_LEVEL, STREAM_LOG_LEVEL


def setup_logger():
    log_dir = FILE_PATH['LOG']
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('autotest')
    logger.setLevel(LOG_LEVEL)

    # File handler
    fh = logging.FileHandler(os.path.join(log_dir, 'test.log'), encoding='utf-8')
    fh.setLevel(LOG_LEVEL)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(STREAM_LOG_LEVEL)

    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logs = setup_logger()