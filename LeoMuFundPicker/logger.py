#!/usr/bin/python

import logging


def get_logger(logger_name, log_file_name="trace.log", log_level=logging.DEBUG):

    logger = logging.getLogger(logger_name)

    handler = logging.FileHandler(log_file_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)-15s #%(lineno)d [%(funcName)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger