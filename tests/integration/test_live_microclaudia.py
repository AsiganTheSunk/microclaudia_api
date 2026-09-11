# -*- coding: utf-8 -*-
"""Live API smoke tests (requires network and valid MicroClaudia credentials)."""

from __future__ import annotations

import pytest
from jsonschema import validate

from microclaudia_api.core.static.microclaudia_exceptions import (
    MicroClaudiaAPIError,
    MicroClaudiaForbiddenError,
    MicroClaudiaRateLimitError,
)
from microclaudia_api.core.static.schemas.microclaudia_schemas import (
    AGENTS_FROM_AGENCY_SCHEMA,
    ALERTS_FROM_AGENCY_SCHEMA,
)

from tests.integration.live_config import discover_live_context

pytestmark = pytest.mark.integration


@pytest.fixture(scope='module')
def live_api(live_credentials):
  from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI

  username, password = live_credentials
  api = MicroClaudiaAPI(username, password)
  assert getattr(api, 'authorization_token', None), 'Login did not set authorization_token'
  return api


@pytest.fixture(scope='module')
def live_ctx(live_api):
  ctx = discover_live_context(live_api)
  if not ctx.get('agency_id'):
    pytest.skip('could not discover agency_id from live API for this account')
  return ctx


def test_live_login_sets_bearer_token(live_api):
  assert live_api.authorization_token.startswith('Bearer ')


def test_live_health_status(live_api):
  assert live_api.health_status() is True


def test_live_get_agents_from_agency(live_api, live_ctx):
  result = live_api.get_agents_from_agency(live_ctx['agency_id'], size=5, page=0)
  assert isinstance(result, dict)
  assert 'collection' in result
  assert 'total' in result
  validate(instance=result, schema=AGENTS_FROM_AGENCY_SCHEMA)


def test_live_get_alerts_from_agency(live_api, live_ctx):
  result = live_api.get_alerts_from_agency(live_ctx['agency_id'], size=5, page=0)
  assert isinstance(result, dict)
  assert 'collection' in result
  validate(instance=result, schema=ALERTS_FROM_AGENCY_SCHEMA)


def test_live_get_tags_from_agency(live_api, live_ctx):
  result = live_api.get_tags_from_agency(live_ctx['agency_id'])
  assert isinstance(result, dict)
  # Live API returns {"tags": ["tag1", ...]}, not a paginated collection envelope.
  assert 'tags' in result
  assert isinstance(result['tags'], list)
  assert len(result['tags']) > 0


def test_live_get_version_agents_stats_from_agency(live_api, live_ctx):
  result = live_api.get_version_agents_stats_from_agency(live_ctx['agency_id'], size=5, page=0)
  assert isinstance(result, list)
  assert len(result) > 0


def test_live_get_instances(live_api):
  import json

  try:
    result = live_api.get_instances()
  except (json.JSONDecodeError, MicroClaudiaForbiddenError, MicroClaudiaRateLimitError, MicroClaudiaAPIError):
    pytest.skip('instances endpoint unavailable for this account')
  if isinstance(result, dict):
    assert 'collection' in result
    assert len(result['collection']) > 0
  else:
    assert isinstance(result, list)
    assert len(result) > 0
