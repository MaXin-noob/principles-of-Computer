# -*- coding: utf-8 -*-
"""
Logging
=======

:dependencies: Python >= 2.7/3.2 **or** (Python <= 2.7/3.2 + logutils_)

.. _logutils: http://pypi.python.org/pypi/logutils

Configuration example (YAML)::

    logging:
        version: 1
        formatters:
            verbose:
                format: '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                datefmt: '%Y-%m-%d %H:%M:%S'
            simple:
                format: '%(levelname)s %(message)s'
                datefmt: '%Y-%m-%d %H:%M:%S'
        handlers:
            console:
                class : logging.StreamHandler
                level: DEBUG
                formatter: simple
                stream  : ext://sys.stdout
            file:
                class : logging.handlers.RotatingFileHandler
                level: DEBUG
                formatter: verbose
                filename: debug.log
                maxBytes: 1048576  # 1 Mb
                backupCount: 5
        root:
            level: DEBUG
            handlers: [console, file]

"""
import logging
try:
    # Python >= 2.7/3.2
    from logging.config import dictConfig
except ImportError:
    # Python <= 2.7/3.2
    from logutils.dictconfig import dictConfig


DEFAULT_CONFIG = {'version': 1}


def setup_logging(conf):
    """
    `logging.dictConfig` is a builtin library in Python 2.7. If it is not
    available, Tool falls back to `logutils.dictconfig.dictConfig`; in this
    case the logutils_ package must be installed.

    :param conf:
        a `dict` containing configuration according to :pep:`391`.
        If ``bool(conf)`` returns False, default configuration is used.

    """
    dictConfig(conf or DEFAULT_CONFIG)
