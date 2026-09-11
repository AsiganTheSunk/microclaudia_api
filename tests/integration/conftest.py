# -*- coding: utf-8 -*-
"""Reload MicroClaudiaAPI with real rate limiting for integration runs."""

from __future__ import annotations

import importlib
import os
import time

import pytest

# MicroClaudiaAPI uses call_rate_limit(limit_per_minute=12) → ~5s between calls.
# Pause between integration tests to avoid HTTP 429 across the suite.
_INTEGRATION_TEST_DELAY_SEC = float(
    os.environ.get('MICROCLAUDIA_INTEGRATION_TEST_DELAY', '10'),
)
# Extra pause before tests that hit /api/tasks (often follow other heavy tests).
_INTEGRATION_TASK_DELAY_SEC = float(
    os.environ.get('MICROCLAUDIA_INTEGRATION_TASK_DELAY', '30'),
)

from tests.conftest import (
    _API_MODULE,
    _config_is_integration_run,
    _purge_microclaudia_api_modules,
)
from tests.integration.live_config import resolve_live_credentials


def pytest_addoption(parser: pytest.Parser) -> None:
  group = parser.getgroup('microclaudia live')
  group.addoption(
      '--live-user',
      action='store',
      default=None,
      help='MicroClaudia username for integration tests (or MICROCLAUDIA_LIVE_USERNAME).',
  )
  group.addoption(
      '--live-password',
      action='store',
      default=None,
      help='MicroClaudia password for integration tests (or MICROCLAUDIA_LIVE_PASSWORD).',
  )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
  if not _config_is_integration_run(config):
    return
  _purge_microclaudia_api_modules()
  importlib.import_module(_API_MODULE)


@pytest.fixture(scope='session')
def live_credentials(pytestconfig: pytest.Config) -> tuple[str, str]:
  """Username/password for live API tests (CLI → env → prompt with capture off)."""
  username = pytestconfig.getoption('--live-user')
  password = pytestconfig.getoption('--live-password')
  try:
    return resolve_live_credentials(username=username, password=password, allow_prompt=False)
  except RuntimeError:
    pass
  capmanager = pytestconfig.pluginmanager.get_plugin('capturemanager')
  if capmanager is None:
    return resolve_live_credentials(username=username, password=password, allow_prompt=True)
  with capmanager.global_and_fixture_disabled():
    return resolve_live_credentials(username=username, password=password, allow_prompt=True)


def _is_task_related_test(request) -> bool:
  return 'task' in request.node.name.lower() or 'export_alerts_csv' in request.node.name.lower()


@pytest.fixture(autouse=True)
def _integration_test_pacing(request):
  """Space out live API calls; longer pause before task-related tests."""
  if request.node.get_closest_marker('integration') is None:
    yield
    return
  if _is_task_related_test(request) and _INTEGRATION_TASK_DELAY_SEC > 0:
    time.sleep(_INTEGRATION_TASK_DELAY_SEC)
  yield
  if _INTEGRATION_TEST_DELAY_SEC > 0:
    time.sleep(_INTEGRATION_TEST_DELAY_SEC)
