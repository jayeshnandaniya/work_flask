"""
Project logger
"""

import logging
import os


LOG_DIR = os.environ.get('LOG_DIR', '')


def setup_logger(logger_name: str, log_file: str, level: int = logging.INFO) -> 'Logger':
    """
    Factory method for creating loggers

    :param logger_name: unique identifier for logger
    :param log_file: specify where to save logs
    :param level: how much logging to do

    :return: A logger
    """
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter(u'%(asctime)s %(message)s')

    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(level)
    if LOG_DIR:
        logger.addHandler(file_handler)
    # logger.addHandler(streamHandler)

    return logger


error_log_path = os.path.join(LOG_DIR, 'error-log.txt')
event_log_path = os.path.join(LOG_DIR, 'event-log.txt')


error_logger = setup_logger('error_logger', error_log_path, level=logging.WARNING)
event_logger = setup_logger('event_logger', event_log_path, level=logging.INFO)
