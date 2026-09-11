# -*- coding: utf-8 -*-
"""Shared pytest fixtures: no-op rate limiting and mock HTTP for MicroClaudiaAPI."""

from __future__ import annotations

import importlib
import json
import os
import sys
from http import HTTPStatus
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

_API_MODULE = 'microclaudia_api.core.microclaudia_api'
_RATE_LIMITER_MODULE = 'microclaudia_api.core.tools.network_call_rate_limiter'


def _purge_microclaudia_api_modules() -> None:
  for name in list(sys.modules):
    if name == 'microclaudia_api' or name.startswith('microclaudia_api.'):
      del sys.modules[name]


def _disable_rate_limiting() -> None:
  """Make call_rate_limit / apply_to_all_methods no-ops before MicroClaudiaAPI loads."""
  rate_limiter = importlib.import_module(_RATE_LIMITER_MODULE)
  rate_limiter.apply_to_all_methods = lambda _decorator: (lambda cls: cls)
  rate_limiter.call_rate_limit = lambda **kwargs: (lambda fn: fn)


def _normalized_argv(config: pytest.Config | None = None) -> str:
  if config is not None:
    parts = [str(a) for a in config.args]
  else:
    parts = sys.argv[1:]
  return ' '.join(parts).replace('\\', '/')


def _config_is_integration_run(config: pytest.Config) -> bool:
  if os.environ.get('MICROCLAUDIA_LIVE_TESTS') == '1':
    return True
  markexpr = (config.getoption('-m', default='') or '').strip()
  if 'not integration' in markexpr:
    return False
  argv = _normalized_argv(config)
  if argv.rstrip('/').endswith('tests/integration'):
    return True
  if '/tests/integration/' in f'{argv}/':
    return True
  if markexpr == 'integration' or markexpr.startswith('integration and'):
    return True
  return False


def _prepare_unit_test_modules() -> None:
  _purge_microclaudia_api_modules()
  _disable_rate_limiting()
  importlib.import_module(_API_MODULE)


def _refresh_api_module_bindings() -> None:
  global microclaudia_api_module, MicroClaudiaAPI
  microclaudia_api_module = importlib.import_module(_API_MODULE)
  MicroClaudiaAPI = microclaudia_api_module.MicroClaudiaAPI


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
  if _config_is_integration_run(config):
    return
  _prepare_unit_test_modules()
  _refresh_api_module_bindings()


if os.environ.get('MICROCLAUDIA_LIVE_TESTS') != '1':
  _prepare_unit_test_modules()

from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI  # noqa: E402
import microclaudia_api.core.microclaudia_api as microclaudia_api_module  # noqa: E402

from tests.fixtures.sample_data import (  # noqa: E402
    AGENCY_ID,
    AUTH_HEADERS,
    INSTANCE_ID,
    SECTOR_ID,
    TASK_ID,
)


class MockHttpResponse:
  """Minimal requests-like response for patched get/post."""

  def __init__(
      self,
      *,
      status_code: int = HTTPStatus.OK,
      json_data: Any = None,
      text: Optional[str] = None,
      content: Optional[bytes] = None,
      headers: Optional[Dict[str, str]] = None,
  ):
    if content is None and json_data is not None:
      content = json.dumps(json_data).encode('utf-8')
    if content is None:
      content = b''
    self.status_code = status_code
    self.content = content
    self.text = text if text is not None else content.decode('utf-8')
    self.headers = headers or {}


@pytest.fixture
def mock_get(mocker):
  import microclaudia_api.core.auth.microclaudia_auth as auth_module

  mock = mocker.patch.object(microclaudia_api_module, 'get')
  mocker.patch.object(auth_module.requests, 'get', mock)
  mock.return_value = MockHttpResponse(json_data={'ok': True})
  return mock


@pytest.fixture
def mock_post(mocker):
  import microclaudia_api.core.auth.microclaudia_auth as auth_module

  mock = mocker.patch.object(microclaudia_api_module, 'post')
  mocker.patch.object(auth_module.requests, 'post', mock)
  mock.return_value = MockHttpResponse(
      headers={
          'Authorization': 'Bearer ' + ('x' * 273),
          'refresh-token': 'refresh-token-value',
      },
  )
  return mock


@pytest.fixture
def mock_ping(mocker):
  ping_result = MagicMock()
  ping_result.status = True
  return mocker.patch.object(microclaudia_api_module, 'ping', return_value=ping_result)


@pytest.fixture
def mock_sleep(mocker):
  return mocker.patch.object(microclaudia_api_module, 'sleep')


@pytest.fixture
def mock_requests(mocker):
  import microclaudia_api.core.auth.microclaudia_auth as auth_module

  return mocker.patch.object(auth_module.requests, 'patch')


@pytest.fixture
def api(mock_get, mock_post, mock_sleep):
  """Authenticated API client with login mocked."""
  client = MicroClaudiaAPI(username='test-user', password='test-pass')
  client.authorization_token = 'Bearer test-token'
  client.refresh_token = 'refresh-token-value'
  return client


@pytest.fixture
def configure_get(mock_get):
  """Return a helper that maps exact URLs (or predicates) to responses."""

  def _configure(mapping: Dict[str, Any]) -> MagicMock:
    def _side_effect(url, **kwargs):
      for key, payload in mapping.items():
        if callable(key):
          if key(url, **kwargs):
            return _as_response(payload)
        elif url == key or url.startswith(key):
          return _as_response(payload)
      raise AssertionError(f'Unexpected GET url: {url!r} kwargs={kwargs!r}')

    mock_get.side_effect = _side_effect
    return mock_get

  return _configure


def _as_response(payload: Any) -> MockHttpResponse:
  if isinstance(payload, MockHttpResponse):
    return payload
  if isinstance(payload, tuple):
    status_code, body = payload
    if isinstance(body, bytes):
      return MockHttpResponse(status_code=status_code, content=body)
    return MockHttpResponse(status_code=status_code, json_data=body)
  return MockHttpResponse(json_data=payload)


def assert_get_called(mock_get, expected_url: str, *, call_index: int = -1, require_auth: bool = True):
  call = mock_get.call_args_list[call_index]
  assert call[0][0] == expected_url
  if require_auth:
    headers = call[1].get('headers') or {}
    assert headers.get('authorization') == 'Bearer test-token'


def assert_json_result(result: Any, expected: Any):
  assert result == expected


@pytest.fixture
def agency_id():
  return AGENCY_ID


@pytest.fixture
def instance_id():
  return INSTANCE_ID


@pytest.fixture
def sector_id():
  return SECTOR_ID


@pytest.fixture
def task_id():
  return TASK_ID


@pytest.fixture
def auth_headers():
  return AUTH_HEADERS.copy()
