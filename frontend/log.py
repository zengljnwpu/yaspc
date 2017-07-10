'''
  Logging wrappers.
'''

import logging


def e(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.error(msg, *args, **kwargs)


def w(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.warning(msg, *args, **kwargs)


def i(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.info(msg, *args, **kwargs)


def d(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.debug(msg, *args, **kwargs)


def set_level(name):
    levels = {"error": logging.ERROR,
              "warn": logging.WARNING,
              "info": logging.INFO,
              "debug": logging.DEBUG}

    if name in levels:
        logging.basicConfig(level=levels[name])


def set_verbosity(lvl):
    levels = (logging.ERROR,
              logging.WARNING,
              logging.INFO,
              logging.DEBUG)

    if lvl > len(levels) - 1:
        lvl = len(levels) - 1
    elif lvl < 0:
        lvl = 0

    logging.basicConfig(level=levels[lvl])
