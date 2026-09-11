# -*- coding: utf-8 -*-
"""Unit tests for validate_json_schema."""

import pytest
from jsonschema import validate

from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaSchemaError
from microclaudia_api.core.static.schemas.microclaudia_schema_validator import validate_json_schema
from microclaudia_api.core.static.schemas.microclaudia_schemas import AGENT_SCHEMA
from tests.fixtures.sample_data import AGENT_RESPONSE


def test_validate_json_schema_returns_payload_on_success():
  result = validate_json_schema(AGENT_RESPONSE, AGENT_SCHEMA, 'get_agent')
  assert result == AGENT_RESPONSE
  validate(instance=result, schema=AGENT_SCHEMA)


def test_validate_json_schema_raises_on_failure():
  with pytest.raises(MicroClaudiaSchemaError) as exc_info:
    validate_json_schema({'unexpected': True}, AGENT_SCHEMA, 'get_agent')
  assert exc_info.value.func_name == 'get_agent'
  assert 'unexpected' in str(exc_info.value.validation_error)


def test_validate_json_schema_accepts_string_func_name():
  result = validate_json_schema(AGENT_RESPONSE, AGENT_SCHEMA, 'my_fn')
  assert result == AGENT_RESPONSE
