# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: FunctionTools Module Imports
from functools import wraps
# Note: Time Module Imports
from time import (
    time,
    sleep
)


class CallCounter:
    """
    This class, will track call timestamps used by the rate limiter.
    """

    def __init__(self):
        """
        This function, will initialize an empty call history.
        """
        self.calls = []

    def add_call(self):
        """
        This function, will record the current timestamp as a call.
        """
        self.calls.append(time())


def call_rate_limit(limit_per_minute):
    """
    This function, will build a decorator that throttles calls to at most limit_per_minute per rolling minute.
    :param limit_per_minute: Maximum number of calls allowed in any 60-second window.
    :return: Decorator that wraps a callable with the rate limit.
    """
    def decorator(func):
        counter = CallCounter()

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time()
            minute_ago = now - 60
            if len([call for call in counter.calls if call > minute_ago]) >= limit_per_minute:
                time_to_wait = 60 - (now - counter.calls[-limit_per_minute])
                print(f'[!]( Call Rate Limit Exceeded ): {time_to_wait} Until Next Request is Send')
                sleep(time_to_wait)
            result = func(*args, **kwargs)
            counter.add_call()
            return result
        return wrapper
    return decorator


def apply_to_all_methods(decorator):
    """
    This function, will build a class decorator that applies another decorator to every callable on the class.
    :param decorator: Decorator applied to each method found on the class.
    :return: Class decorator that mutates the class in place and returns it.
    """
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate
