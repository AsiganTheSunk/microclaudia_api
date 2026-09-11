# -*- coding: utf-8 -*-
"""
Live probe of every public MicroClaudiaAPI method.

Run: python -m pytest tests/integration/test_live_all_api_methods.py -m integration -v
"""

from __future__ import annotations

import pytest
from jsonschema import validate

from microclaudia_api.core.static.schemas.microclaudia_schemas import (
    AGENTS_FROM_AGENCY_SCHEMA,
    ALERTS_FROM_AGENCY_SCHEMA,
    VACCINES_FROM_AGENCY_SCHEMA,
)
from tests.integration.live_config import discover_live_context
from tests.integration.live_helpers import (
    assert_dict_payload,
    assert_list_payload,
    assert_ok,
    probe,
)

pytestmark = [pytest.mark.integration, pytest.mark.live_all_methods]


@pytest.fixture(scope='module')
def live_api(live_credentials):
  from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI

  username, password = live_credentials
  api = MicroClaudiaAPI(username, password)
  assert getattr(api, 'authorization_token', None), 'login failed: no authorization_token'
  return api


@pytest.fixture(scope='module')
def ctx(live_api):
  """Discover instance/sector/agent IDs from live responses (same approach as the demo script)."""
  ctx = discover_live_context(live_api)
  agency_id = ctx['agency_id']
  instance_id = ctx['instance_id']
  sector_id = ctx['sector_id']
  agent_id = None

  if not agency_id:
    pytest.skip('could not discover agency_id from live API for this account')

  alerts = probe(
      'get_alerts_from_agency',
      lambda: live_api.get_alerts_from_agency(agency_id, size=1, page=0),
  )
  if alerts.status == 'ok' and isinstance(alerts.result, dict):
    collection = alerts.result.get('collection') or []
    if collection:
      agency = collection[0].get('agency') or {}
      instance_id = agency.get('instanceId')
      sector_id = agency.get('sector')

  agents = probe(
      'get_agents_from_agency',
      lambda: live_api.get_agents_from_agency(agency_id, size=1, page=0),
  )
  if agents.status == 'ok' and isinstance(agents.result, dict):
    collection = agents.result.get('collection') or []
    if collection:
      agent_id = collection[0].get('id')

  if not instance_id or not sector_id:
    sectors = probe('get_sectors', live_api.get_sectors)
    if sectors.status == 'ok':
      payload = sectors.result
      if isinstance(payload, dict):
        collection = payload.get('collection') or []
        if collection:
          instance_id = instance_id or collection[0].get('instanceId')
          sector_id = sector_id or collection[0].get('id')

  return {
      'agency_id': agency_id,
      'agency_servers': ctx['agency_servers'],
      'instance_id': instance_id,
      'sector_id': sector_id,
      'agent_id': agent_id,
  }


def _require_ctx_id(ctx, key: str):
  value = ctx.get(key)
  if not value:
    pytest.skip(f'could not discover {key} from live API for this account')
  return value


# --- Auth / health ---


def test_live_init_and_login(live_api, live_credentials):
  username, _password = live_credentials
  assert live_api.username == username
  assert live_api.authorization_token.startswith('Bearer ')


def test_live_health_status(live_api):
  assert live_api.health_status() is True


def test_live_login(live_api, live_credentials):
  username, password = live_credentials
  token, refresh = live_api.login(username, password)
  assert token.startswith('Bearer ')
  assert refresh


def test_live_auth_refresh(live_api):
  outcome = probe('auth_refresh', live_api.auth_refresh)
  assert_ok(outcome)
  assert isinstance(outcome.result, dict)
  assert live_api.authorization_token.startswith('Bearer ')
  assert live_api.refresh_token


# --- Agency stats (groupBy) ---

def test_live_get_agents_last_version(live_api):
  outcome = probe('get_agents_last_version', live_api.get_agents_last_version)
  assert_ok(outcome, skip_transient=True)



@pytest.mark.parametrize(
    'method',
    [
        'get_version_agents_stats_from_agency',
        'get_os_agents_stats_from_agency',
        'get_status_agents_stats_from_agency',
        'get_vaccine_stats_from_alerts',
        'get_computer_stats_from_alerts',
    ],
)
def test_live_agency_stats_count(live_api, ctx, method):
  fn = getattr(live_api, method)
  outcome = probe(method, lambda: fn(ctx['agency_id'], size=5, page=0))
  assert_list_payload(outcome)


# --- Agency collections ---


def test_live_get_agents_from_agency(live_api, ctx):
  outcome = probe(
      'get_agents_from_agency',
      lambda: live_api.get_agents_from_agency(
          ctx['agency_id'], size=5, page=0, sort_by='version', order_by='asc',
      ),
  )
  assert_dict_payload(outcome, keys=('total', 'collection'))
  validate(instance=outcome.result, schema=AGENTS_FROM_AGENCY_SCHEMA)


def test_live_get_agents_from_agency_with_default_filter(live_api, ctx):
  outcome = probe(
      'get_agents_from_agency',
      lambda: live_api.get_agents_from_agency(
          ctx['agency_id'], size=5, page=0, filter_by='osFamily:windows',
      ),
  )
  assert_dict_payload(outcome, keys=('total', 'collection'))
  validate(instance=outcome.result, schema=AGENTS_FROM_AGENCY_SCHEMA)


def test_live_get_alerts_from_agency(live_api, ctx):
  outcome = probe(
      'get_alerts_from_agency',
      lambda: live_api.get_alerts_from_agency(ctx['agency_id'], size=5, page=0),
  )
  assert_dict_payload(outcome, keys=('total', 'collection'))
  validate(instance=outcome.result, schema=ALERTS_FROM_AGENCY_SCHEMA)


def test_live_get_vaccines_from_agency(live_api, ctx):
  outcome = probe(
      'get_vaccines_from_agency',
      lambda: live_api.get_vaccines_from_agency(ctx['agency_id'], size=5, page=0),
  )
  assert_dict_payload(outcome, keys=('total', 'collection'))
  validate(instance=outcome.result, schema=VACCINES_FROM_AGENCY_SCHEMA)


def test_live_get_tags_from_agency(live_api, ctx):
  outcome = probe(
      'get_tags_from_agency',
      lambda: live_api.get_tags_from_agency(ctx['agency_id']),
  )
  assert_ok(outcome)
  # API returns {"tags": [...]} not paginated envelope
  assert 'tags' in outcome.result
  assert isinstance(outcome.result['tags'], list)


# --- Global stats ---


@pytest.mark.parametrize(
    'method,kwargs',
    [
        ('get_os_stats_from_agents', {'size': 5, 'page': 0}),
        ('get_versions_stats_from_agents', {'size': 5, 'page': 0}),
        ('get_status_stats_from_agents', {'size': 5, 'page': 0}),
        ('get_computer_stats_from_alerts', {'size': 5, 'page': 0}),
        ('get_vaccine_stats_from_alerts', {'size': 5, 'page': 0}),
    ],
)
def test_live_global_stats_count(live_api, ctx, method, kwargs):
  fn = getattr(live_api, method)
  if method == 'get_computer_stats_from_alerts':
    kwargs = {**kwargs, 'agency_id': ctx['agency_id']}
  if method == 'get_vaccine_stats_from_alerts':
    kwargs = {**kwargs, 'agency_id': ctx['agency_id']}
  outcome = probe(method, lambda: fn(**kwargs))
  if method == 'get_status_stats_from_agents':
    assert_list_payload(outcome, min_len=0, skip_transient=True)
    return
  assert_list_payload(outcome, skip_transient=True)


def test_live_get_total_stats(live_api):
  outcome = probe('get_total_stats', lambda: live_api.get_total_stats())
  assert_ok(outcome)
  assert isinstance(outcome.result, dict)


def test_live_get_total_stats_evolution(live_api):
  outcome = probe(
      'get_total_stats_evolution',
      lambda: live_api.get_total_stats_evolution(evolution_id=7),
  )
  assert_ok(outcome)


def test_live_get_alerts(live_api):
  outcome = probe(
      'get_alerts',
      lambda: live_api.get_alerts(size=5, page=0, filter_by='status:1'),
  )
  assert_ok(outcome)


# --- Instance / sector ---


def test_live_get_agencies_from_instance(live_api, ctx):
  instance_id = _require_ctx_id(ctx, 'instance_id')
  outcome = probe(
      'get_agencies_from_instance',
      lambda: live_api.get_agencies_from_instance(instance_id, size=50),
  )
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip(f"{outcome.method}: {outcome.detail}")
  assert_ok(outcome)


def test_live_get_sectors_from_instance(live_api, ctx):
  instance_id = _require_ctx_id(ctx, 'instance_id')
  outcome = probe(
      'get_sectors_from_instance',
      lambda: live_api.get_sectors_from_instance(instance_id, size=10, page=0),
  )
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip(f"{outcome.method}: forbidden or empty for this account")
  assert_ok(outcome)


def test_live_get_instances(live_api):
  outcome = probe('get_instances', live_api.get_instances)
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip('get_instances: 403 or empty for this account')
  assert_ok(outcome)
  if isinstance(outcome.result, list):
    assert len(outcome.result) > 0
  else:
    assert_dict_payload(outcome, keys=('collection',))
    assert len(outcome.result['collection']) > 0


def test_live_get_instances_filtered(live_api):
  outcome = probe(
      'get_instances',
      lambda: live_api.get_instances(size=50, filter_by='type:2'),
  )
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip('get_instances: 403 or empty for this account')
  assert_ok(outcome)
  if isinstance(outcome.result, list):
    return
  assert_dict_payload(outcome, keys=('collection',))


def test_live_get_sectors(live_api):
  outcome = probe('get_sectors', live_api.get_sectors)
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip('get_sectors: forbidden or empty for this account')
  assert_ok(outcome)


def test_live_get_agencies_from_sectors(live_api, ctx):
  sector_id = _require_ctx_id(ctx, 'sector_id')
  outcome = probe(
      'get_agencies_from_sectors',
      lambda: live_api.get_agencies_from_sector(sector_id, size=10, page=0),
  )
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip(f"{outcome.method}: {outcome.detail}")
  assert_ok(outcome)


def test_live_get_instance(live_api, ctx):
  instance_id = _require_ctx_id(ctx, 'instance_id')
  outcome = probe('get_instance', lambda: live_api.get_instance(instance_id))
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip(f"{outcome.method}: {outcome.detail}")
  assert_ok(outcome)
  assert isinstance(outcome.result, dict)
  assert outcome.result.get('id') == instance_id


def test_live_get_sector(live_api, ctx):
  sector_id = _require_ctx_id(ctx, 'sector_id')
  outcome = probe('get_sector', lambda: live_api.get_sector(sector_id))
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip(f"{outcome.method}: {outcome.detail}")
  assert_ok(outcome)
  assert isinstance(outcome.result, dict)
  assert outcome.result.get('id') == sector_id


def test_live_get_agent(live_api, ctx):
  agent_id = _require_ctx_id(ctx, 'agent_id')
  outcome = probe('get_agent', lambda: live_api.get_agent(agent_id))
  assert_ok(outcome, skip_transient=True)
  assert isinstance(outcome.result, dict)
  assert outcome.result.get('id') == agent_id


def test_live_get_tags_from_agent(live_api, ctx):
  agent_id = _require_ctx_id(ctx, 'agent_id')
  outcome = probe('get_tags_from_agent', lambda: live_api.get_tags_from_agent(agent_id))
  assert_ok(outcome, skip_transient=True)
  assert isinstance(outcome.result, list)


# --- Catalog / platform ---


@pytest.mark.parametrize(
    'method',
    [
        'get_version',
        'get_oses',
        'get_user_roles',
        'get_stats_news',
        'get_deployments_sector_stats',
    ],
)
def test_live_platform_catalog(live_api, method):
  fn = getattr(live_api, method)
  outcome = probe(method, fn)
  assert_ok(outcome, skip_transient=True)


def test_live_get_users(live_api):
  outcome = probe('get_users', lambda: live_api.get_users(size=10))
  if outcome.status in ('empty_body', 'forbidden'):
    pytest.skip(f"{outcome.method}: {outcome.detail}")
  assert_ok(outcome, skip_transient=True)


def test_live_get_vaccines_global(live_api):
  outcome = probe('get_vaccines', lambda: live_api.get_vaccines(size=10))
  assert_ok(outcome, skip_transient=True)
  assert isinstance(outcome.result, dict)
  assert 'collection' in outcome.result


def test_live_get_stats_helper(live_api, ctx):
  outcome = probe(
      'get_stats',
      lambda: live_api.get_stats('agents', 'os', agency_id=ctx['agency_id'], size=5, page=0),
  )
  assert_list_payload(outcome, skip_transient=True)


# --- Agents pagination ---


def test_live_get_all_agents_stats_from_agency(live_api, ctx):
  # max_pages=1: first page only; delay=0 avoids inter-page countdown in live runs.
  outcome = probe(
      'get_all_agents_stats_from_agency',
      lambda: live_api.get_all_agents_from_agency(
          ctx['agency_id'], size=500, max_pages=1, delay=0,
      ),
  )
  assert_ok(outcome, allow_none=False)
  assert_dict_payload(outcome, keys=('total', 'size', 'page', 'collection'))
