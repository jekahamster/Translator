import logging

from defines import LOG_FILE
from defines import LOG_FORMAT
from defines import LOG_DATE_TIME_FORMAT
from defines import LOG_LEVEL


def _handler_set_up(handler):
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_TIME_FORMAT))
    return handler


def get_file_handler():
    handler = logging.FileHandler(LOG_FILE)
    return _handler_set_up(handler)


def get_stream_handler():
    handler = logging.StreamHandler()
    return _handler_set_up(handler)


def get_logger(name):
    logger = logging.Logger(name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger

    