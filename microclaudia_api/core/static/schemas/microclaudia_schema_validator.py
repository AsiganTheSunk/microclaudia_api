# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: Typing Module Imports
from typing import Any, Union
# Note: Json Schema Module Imports
from jsonschema import validate
from jsonschema.exceptions import (
    SchemaError,
    ValidationError
)
# Note: MicroClaudia API Module Imports
from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaSchemaError


def _caller_name(func: Union[Any, str]) -> str:
    if isinstance(func, str):
        return func
    return getattr(func, '__name__', repr(func))


def validate_json_schema(json_result: dict | list, json_schema: dict, func: Union[Any, str]) -> Any:
    """
    This function, will validate a JSON payload against a jsonschema definition.
    :param json_result: Parsed JSON object to validate.
    :param json_schema: jsonschema dict describing the expected structure.
    :param func: Callable or function name used in error messages.
    :return: json_result when validation succeeds.
    :raises MicroClaudiaSchemaError: When validation fails.
    """
    func_name = _caller_name(func)
    try:
        validate(instance=json_result, schema=json_schema)
        return json_result
    except (ValidationError, SchemaError) as error:
        raise MicroClaudiaSchemaError(func_name, error) from error
