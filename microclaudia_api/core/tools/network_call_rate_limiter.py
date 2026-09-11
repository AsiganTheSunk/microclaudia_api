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
    def __init__(self):
        self.calls = []

    def add_call(self):
        self.calls.append(time())


def call_rate_limit(limit_per_minute):
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
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate
