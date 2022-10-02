import logging
from rich import print as rprint

logger = logging.getLogger()


def set_logging_level(level):
    logger.setLevel(level)


def debug_log(*args):
    if logger.getEffectiveLevel() == logging.DEBUG:
        rprint(args)
