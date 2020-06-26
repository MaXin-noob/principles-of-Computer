# -*- coding: utf-8 -*-
#
#  Copyright (c) 2011 Andrey Mikhaylenko and contributors
#
#  This file is part of Tool.
#
#  Tool is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#
"""
Decorators
==========

This module contains general-purpose decorators.

:state: stable
:dependencies: none

"""
from functools import wraps
from time import sleep

__all__ = ['retry']


def retry(catch=Exception, wait=.1, slowdown=1, max_wait=5, retries=10):
    """ Decorator. Calls given function again on certain condition and
    gradually slows down at given rate until the duration exceeds given limit.

    :param catch:
        An exception class (or a sequence of them). If wrapped function raises
        this exception, it is called again.
    :param wait:
        How much to wait (in seconds) on the first retry. Default is ``0.1``.
        Further durations depend on `slowdown` rate.
    :param slowdown:
        Slowdown rate. The waiting duration will be multiplied by this
        value on each retry.
        Negative values make the attempts occur faster and faster.
        Default is ``1`` (i.e. the duration is the same for all attempts).
    :param max_wait:
        The maximum allowed total waiting duration (in seconds). If the
        duration is exceeded, the original exception is raised.
        Default is ``5``.
    :param retries:
        The maximum allowed amount of attempts to run the function again.
        Default is ``10``.

    Usage::

        @retry_slowdown()
        def test():
            raise KeyError('Oops, I did it again!')

    Let's be more specific::

        @retry_slowdown(KeyError, initial=.5, rate=2)
        def test():
            raise KeyError('Oops, I did it again!')

    """
    assert issubclass(catch, Exception) or isinstance(catch, (list, tuple))
    def wrapper(f):
        @wraps(f)
        def slowdown_wrapper(*args, **kwargs):
            # TODO: let user define maximum *number* of attempts
            last_duration = 0
            total_duration = 0
            attempts_cnt = 0
            while True:
                try:
                    # TODO: check returned value and raise error
                    # on user-defined condition
                    return f(*args, **kwargs)
                except catch as e:
                    if retries <= attempts_cnt:
                        log.error('Exceeded maximum number of retries.')
                        raise e
                    duration = last_duration * slowdown if last_duration else wait
                    total_duration += duration
                    if max_wait < total_duration:
                        log.error('Exceeded maximum waiting duration.')
                        raise e
                    log.warn('Catched {e.__class__.__name__} "{e}". '
                             'Retrying in {wait}s...'.format(e=e, wait=duration))
                    last_duration = duration
                    attempts_cnt += 1
                    sleep(duration)
        return slowdown_wrapper
    return wrapper
