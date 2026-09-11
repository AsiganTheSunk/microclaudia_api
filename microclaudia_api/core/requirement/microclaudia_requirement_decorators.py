# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: Regex Module Imports
from re import match
# Note: Typing Module Imports
from typing import Any
# Note: FuncTools Module Imports
from functools import wraps
# Note: Requirement Constants Module Imports
from microclaudia_api.core.requirement.microclaudia_requirement_constants import MICROCLAUDIA_ID_PATTERN
# Note: Microclaudia Exceptions Module Imports
from microclaudia_api.core.static.microclaudia_exceptions import (
    MicroClaudiaAgencyError,
    MicroClaudiaAgentError,
    MicroClaudiaSectorError,
    MicroClaudiaInstanceError,
    MicroClaudiaPatternError,
)

def _get_first_arg_or_kwarg(args, kwargs, key: str):
    """
    This function, will resolve a required id from the first positional argument after self, or from a named kwarg.
    :param args: Positional arguments passed to the decorated method.
    :param kwargs: Keyword arguments passed to the decorated method.
    :param key: Kwarg name to read when the value was not passed positionally (e.g. agency_id).
    :return: The resolved value, or None when it is missing.
    """
    if len(args) >= 2:
        return args[1]
    if key in kwargs:
        return kwargs.get(key)
    return None


def require_microclaudia_agency_id(func):
    """
    This function, will wrap an API method and require a non-None agency_id as the first argument after self.
    :param func: Callable to decorate (expects agency_id at args[1]).
    :return: Wrapped function that raises MicroClaudiaAgencyError when agency_id is None.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        agency_id = _get_first_arg_or_kwarg(args, kwargs, 'agency_id')
        if agency_id is None:
            raise MicroClaudiaAgencyError('[!]( < agency_id > Requirement ): Cannot Be "None"')
        return func(*args, **kwargs)
    return wrapper


def require_sector_id(func):
    """
    This function, will wrap an API method and require a non-None sector_id as the first argument after self.
    :param func: Callable to decorate (expects sector_id at args[1]).
    :return: Wrapped function that raises MicroClaudiaSectorError when sector_id is None.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sector_id = _get_first_arg_or_kwarg(args, kwargs, 'sector_id')
        if sector_id is None:
            raise MicroClaudiaSectorError('[!]( < sector_id > Requirement ): Cannot Be "None"')
        return func(*args, **kwargs)
    return wrapper


def require_instance_id(func):
    """
    This function, will wrap an API method and require a non-None instance_id as the first argument after self.
    :param func: Callable to decorate (expects instance_id at args[1]).
    :return: Wrapped function that raises MicroClaudiaInstanceError when instance_id is None.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        instance_id = _get_first_arg_or_kwarg(args, kwargs, 'instance_id')
        if instance_id is None:
            raise MicroClaudiaInstanceError('[!]( < instance_id > Requirement ): Cannot Be "None"')
        return func(*args, **kwargs)
    return wrapper


def require_agent_id(func):
    """
    This function, will wrap an API method and require a non-None agent_id as the first argument after self.
    :param func: Callable to decorate (expects agent_id at args[1]).
    :return: Wrapped function that raises MicroClaudiaInstanceError when agent_id is None.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        agent_id = _get_first_arg_or_kwarg(args, kwargs, 'agent_id')
        if agent_id is None:
            raise MicroClaudiaAgentError('[!]( < agent_id > Requirement ): Cannot Be "None"')
        return func(*args, **kwargs)
    return wrapper


def require_microclaudia_valid_id_pattern(func, pattern: str = MICROCLAUDIA_ID_PATTERN) -> Any:
    """
    This function, will wrap an API method and validate that the id argument matches the MicroClaudia id regex.
    :param func: Callable to decorate (expects id at args[1]).
    :param pattern: Regular expression that the id must match (defaults to MICROCLAUDIA_ID_PATTERN).
    :return: Wrapped function that raises MicroClaudiaPatternError when the id does not match.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        value = None
        if len(args) >= 2:
            value = args[1]
        else:
            for key in ('agency_id', 'sector_id', 'instance_id', 'agent_id', 'id'):
                if key in kwargs:
                    value = kwargs.get(key)
                    break
        if value is None:
            raise MicroClaudiaPatternError(f'Argument does not match pattern: {pattern}')
        if not match(pattern, value):
            raise MicroClaudiaPatternError(f'Argument does not match pattern: {pattern}')
        return func(*args, **kwargs)
    return wrapper
