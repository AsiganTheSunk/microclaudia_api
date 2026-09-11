# -*- coding: utf-8 -*-
"""Contract tests: each MicroClaudiaAPI method calls the expected URL and returns parsed data."""

from __future__ import annotations

import json
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from jsonschema import validate

from microclaudia_api.core.microclaudia_api_tools import add_query_params
from microclaudia_api.core.static.microclaudia_uri_constants import (
    MICROCLAUDIA_REQUEST_TIMEOUT,
    MICROCLAUDIA_AGENCIES_FROM_INSTANCE,
    MICROCLAUDIA_AGENCY_AGENT_CONTENT,
    MICROCLAUDIA_AGENCY_STATS_CONTENT,
    MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA,
    MICROCLAUDIA_AGENCY_TAGS_CONTENT,
    MICROCLAUDIA_AGENCY_VACCINE_CONTENT,
    MICROCLAUDIA_ALERTS_CSV,
    MICROCLAUDIA_ALERTS,
    MICROCLAUDIA_INSTANCE_LIST,
    MICROCLAUDIA_INSTANCE_SECTOR_CONTENT,
    MICROCLAUDIA_SECTOR_AGENCIES_CONTENT,
    MICROCLAUDIA_SECTOR_LIST,
    MICROCLAUDIA_STATS_EVOLUTION,
    MICROCLAUDIA_TASK,
    MICROCLAUDIA_TASKS,
    MICROCLAUDIA_AUTH_REFRESH,
    MICROCLAUDIA_OSES,
    MICROCLAUDIA_STATS_NEWS,
    MICROCLAUDIA_TOTAL_STATS,
    MICROCLAUDIA_URL,
    MICROCLAUDIA_USER_ROLES,
    MICROCLAUDIA_USERS,
    MICROCLAUDIA_VERSION,
    MICROCLAUDIA_AGENTS_LAST_VERSION,
    MICROCLAUDIA_INSTANCE,
    MICROCLAUDIA_SECTOR,
    MICROCLAUDIA_VACCINES,
    MICROCLAUDIA_AGENT_CONTENT,
    MICROCLAUDIA_DEPLOYMENTS_SECTOR_STATS,
)
from microclaudia_api.core.static.schemas.microclaudia_schemas import (
    AGENTS_FROM_AGENCY_SCHEMA,
    ALERTS_FROM_AGENCY_SCHEMA,
    AGENTS_LAST_VERSION_SCHEMA,
    AUTH_REFRESH_SCHEMA,
    OSES_SCHEMA,
    STATS_COUNT_SCHEMA,
    STATS_NEWS_SCHEMA,
    USER_ROLES_SCHEMA,
    USERS_SCHEMA,
    VERSION_SCHEMA,
    INSTANCE_SCHEMA,
    SECTOR_SCHEMA,
    VACCINES_SCHEMA,
    AGENT_SCHEMA,
)
from tests.conftest import MockHttpResponse, assert_get_called
from tests.fixtures.sample_data import (
    AGENCY_ID,
    AGENT_ID,
    AGENTS_PAGE,
    ALERTS_PAGE,
    AUTH_REFRESH_RESPONSE,
    EVOLUTION_STATS,
    INSTANCE_ID,
    OSES_RESPONSE,
    PAGINATED_EMPTY,
    REFRESH_TOKEN_HEADER,
    SECTOR_ID,
    STATS_COUNT_RESPONSE,
    STATS_NEWS_RESPONSE,
    TAGS_PAGE,
    TOTAL_STATS,
    USER_ROLES_RESPONSE,
    USERS_PAGE,
    VACCINES_PAGE,
    VERSION_RESPONSE,
    AGENTS_LAST_VERSION_RESPONSE,
    INSTANCE_RESPONSE,
    SECTOR_RESPONSE,
    GLOBAL_VACCINES_PAGE,
    AGENT_RESPONSE,
    DEPLOYMENTS_SECTOR_STATS_RESPONSE,
)


def _assert_validates_schema(instance, schema):
  validate(instance=instance, schema=schema)


@pytest.mark.parametrize(
    'method_name,positional_args,extra_kwargs,expected_url,response_body',
    [
        (
            'get_version_agents_stats_from_agency',
            (AGENCY_ID,),
            {'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'agents', 'version', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_os_agents_stats_from_agency',
            (AGENCY_ID,),
            {'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'agents', 'os', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_status_agents_stats_from_agency',
            (AGENCY_ID,),
            {'size': 50, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'agents', 'status', 50, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_vaccine_stats_from_alerts',
            (AGENCY_ID,),
            {'size': 100, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'alerts', 'vaccine', 100, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_computer_stats_from_alerts',
            (AGENCY_ID,),
            {'size': 100, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'alerts', 'computer', 100, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_vaccines_from_agency',
            (AGENCY_ID,),
            {'size': 10, 'page': 0},
            MICROCLAUDIA_AGENCY_VACCINE_CONTENT(AGENCY_ID, 10, 0),
            VACCINES_PAGE,
        ),
        (
            'get_tags_from_agency',
            (AGENCY_ID,),
            {},
            MICROCLAUDIA_AGENCY_TAGS_CONTENT(AGENCY_ID),
            TAGS_PAGE,
        ),
        (
            'get_sectors_from_instance',
            (INSTANCE_ID,),
            {'size': 10, 'page': 0},
            MICROCLAUDIA_INSTANCE_SECTOR_CONTENT(INSTANCE_ID, 10, 0),
            PAGINATED_EMPTY,
        ),
        (
            'get_os_stats_from_agents',
            (),
            {'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT('agents', 'os', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_versions_stats_from_agents',
            (),
            {'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT('agents', 'version', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_status_stats_from_agents',
            (),
            {'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT('agents', 'status', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_computer_stats_from_alerts',
            (AGENCY_ID,),
            {'size': 8, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'alerts', 'computer', 8, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_vaccine_stats_from_alerts',
            (AGENCY_ID,),
            {'size': 8, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'alerts', 'vaccine', 8, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_stats',
            (),
            {'section': 'agents', 'group_by': 'os', 'agency_id': AGENCY_ID, 'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(AGENCY_ID, 'agents', 'os', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_stats',
            (),
            {'section': 'agents', 'group_by': 'version', 'size': 5, 'page': 0},
            MICROCLAUDIA_AGENCY_STATS_CONTENT('agents', 'version', 5, 0),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_stats',
            (),
            {'section': 'deployments', 'group_by': 'sector', 'size': 5},
            MICROCLAUDIA_DEPLOYMENTS_SECTOR_STATS(5),
            STATS_COUNT_RESPONSE,
        ),
        (
            'get_total_stats',
            (),
            {},
            MICROCLAUDIA_TOTAL_STATS,
            TOTAL_STATS,
        ),
        (
            'get_total_stats_evolution',
            (),
            {'evolution_id': 7},
            MICROCLAUDIA_STATS_EVOLUTION(7),
            EVOLUTION_STATS,
        ),
        (
            'get_agencies_from_instance',
            (INSTANCE_ID,),
            {'size': 200},
            MICROCLAUDIA_AGENCIES_FROM_INSTANCE(INSTANCE_ID, 200),
            PAGINATED_EMPTY,
        ),
    ],
)
def test_api_methods_url_and_json_return(
    api, mock_get, method_name, positional_args, extra_kwargs, expected_url, response_body,
):
  mock_get.return_value = MockHttpResponse(json_data=response_body)
  method = getattr(api, method_name)
  result = method(*positional_args, **extra_kwargs)
  assert result == response_body
  assert_get_called(mock_get, expected_url)


def test_get_agents_from_agency_validates_schema_and_returns(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=AGENTS_PAGE)
  result = api.get_agents_from_agency(AGENCY_ID, size=10, page=0)
  assert result == AGENTS_PAGE
  validate(instance=result, schema=AGENTS_FROM_AGENCY_SCHEMA)
  assert_get_called(mock_get, MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 10, 0))


def test_get_agents_from_agency_raises_on_invalid_schema(api, mock_get):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaSchemaError

  mock_get.return_value = MockHttpResponse(json_data={'unexpected': True})
  with pytest.raises(MicroClaudiaSchemaError) as exc_info:
    api.get_agents_from_agency(AGENCY_ID)
  assert exc_info.value.func_name == 'get_agents_from_agency'


def test_get_agent_raises_on_invalid_schema(api, mock_get):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaSchemaError

  mock_get.return_value = MockHttpResponse(json_data={'unexpected': True})
  with pytest.raises(MicroClaudiaSchemaError) as exc_info:
    api.get_agent(AGENT_ID)
  assert exc_info.value.func_name == 'get_agent'


def test_get_total_stats_raises_on_invalid_schema(api, mock_get):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaSchemaError

  mock_get.return_value = MockHttpResponse(json_data={'unexpected': True})
  with pytest.raises(MicroClaudiaSchemaError) as exc_info:
    api.get_total_stats()
  assert exc_info.value.func_name == 'get_total_stats'


def test_get_agents_from_agency_uses_agents_endpoint(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=AGENTS_PAGE)
  result = api.get_agents_from_agency(
      AGENCY_ID, size=50, page=0, sort_by='version', order_by='asc',
  )
  assert result == AGENTS_PAGE
  called_url = mock_get.call_args[0][0]
  assert '/agents?' in called_url
  assert '/alerts?' not in called_url
  assert 'sortBy=version' in called_url
  assert 'orderBy=asc' in called_url


def test_get_alerts_from_agency_uses_alerts_endpoint_and_schema(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=ALERTS_PAGE)
  result = api.get_alerts_from_agency(
      AGENCY_ID, size=10, page=0, filter_by='status:1',
  )
  assert result == ALERTS_PAGE
  validate(instance=result, schema=ALERTS_FROM_AGENCY_SCHEMA)
  called_url = mock_get.call_args[0][0]
  assert '/alerts?' in called_url
  assert 'filter=status%3A1' in called_url


def test_get_instances(api, mock_get):
  body = [{'id': INSTANCE_ID}]
  mock_get.return_value = MockHttpResponse(json_data=body)
  assert api.get_instances() == body
  assert_get_called(mock_get, MICROCLAUDIA_INSTANCE_LIST)


def test_get_instances_with_default_filter(api, mock_get):
  body = [{'id': INSTANCE_ID}]
  mock_get.return_value = MockHttpResponse(json_data=body)
  assert api.get_instances(size=50, filter_by='type:2') == body
  assert_get_called(
      mock_get,
      add_query_params(f'{MICROCLAUDIA_INSTANCE_LIST}?size=50', defaultFilter='type:2'),
  )


def test_get_sectors(api, mock_get):
  body = [{'id': SECTOR_ID}]
  mock_get.return_value = MockHttpResponse(json_data=body)
  assert api.get_sectors() == body
  assert_get_called(mock_get, MICROCLAUDIA_SECTOR_LIST)


def test_get_alerts_global(api, mock_get):
  body = ALERTS_PAGE
  mock_get.return_value = MockHttpResponse(json_data=body)
  result = api.get_alerts(size=6, page=0, filter_by='status:1')
  assert result == body
  called_url = mock_get.call_args[0][0]
  assert called_url.startswith(f'{MICROCLAUDIA_ALERTS(6, 0).split("?")[0]}')
  assert 'filter=status%3A1' in called_url


def test_health_status_true(api, mock_get, mock_ping):
  mock_get.return_value = MockHttpResponse(status_code=HTTPStatus.OK)
  assert api.health_status() is True
  mock_ping.assert_called_once()
  assert_get_called(mock_get, MICROCLAUDIA_URL, require_auth=False)


def test_health_status_false_when_ping_fails(api, mock_get, mock_ping):
  mock_ping.return_value.status = False
  assert api.health_status() is False
  mock_get.assert_not_called()


def test_login_returns_tokens(api, mock_post):
  token, refresh = api.login('user', 'pass')
  assert token.startswith('Bearer ')
  assert refresh == 'refresh-token-value'
  assert api.authorization_token == token
  assert api.refresh_token == refresh
  mock_post.assert_called()
  assert mock_post.call_args[0][0].endswith('/login')


def test_init_raises_when_login_returns_no_response(mock_post):
  from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaAuthError

  mock_post.return_value = None
  with pytest.raises(MicroClaudiaAuthError, match='no response'):
    MicroClaudiaAPI('user', 'pass')


def test_init_raises_when_login_returns_forbidden(mock_post):
  from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaAuthError

  mock_post.return_value = MagicMock(status_code=HTTPStatus.FORBIDDEN, headers={})
  with pytest.raises(MicroClaudiaAuthError, match='403'):
    MicroClaudiaAPI('user', 'pass')


def test_export_alerts_csv_waits_for_named_task_not_first_complete(api, mock_get, mock_sleep, tmp_path):
  alerts_task_id = 'alerts-csv-id'
  alerts_csv = b'id;msg\n01a07b4f;exported\n'
  out = tmp_path / 'alerts.csv'
  equipos = {'id': 'equipos-csv-id', 'name': 'Equipos.csv', 'complete': True}
  pending = {'id': alerts_task_id, 'name': 'Alertas.csv', 'complete': False}
  complete = {'id': alerts_task_id, 'name': 'Alertas.csv', 'complete': True}
  mock_get.side_effect = [
      MockHttpResponse(content=b''),
      MockHttpResponse(json_data=[equipos, pending]),
      MockHttpResponse(json_data=[equipos, complete]),
      MockHttpResponse(content=alerts_csv),
  ]
  result = api.export_alerts_csv(output_path=str(out), pooling_interval=0, max_retries=2)
  assert result is True
  assert out.read_bytes() == alerts_csv
  called_urls = [call[0][0] for call in mock_get.call_args_list]
  assert called_urls == [
      MICROCLAUDIA_ALERTS_CSV,
      MICROCLAUDIA_TASKS,
      MICROCLAUDIA_TASKS,
      MICROCLAUDIA_TASK(alerts_task_id),
  ]


def test_export_alerts_csv_returns_false_when_named_task_never_completes(api, mock_get, mock_sleep):
  mock_get.side_effect = [
      MockHttpResponse(content=b''),
      MockHttpResponse(json_data=[{'id': 'alerts-csv-id', 'name': 'Alertas.csv', 'complete': False}]),
  ]
  assert api.export_alerts_csv(pooling_interval=0, max_retries=0) is False


def test_get_all_agents_stats_from_agency_returns_merged_collection(api, mock_get, mock_sleep):
  mock_get.return_value = MockHttpResponse(json_data={**AGENTS_PAGE, 'total': 1})
  result = api.get_all_agents_from_agency(AGENCY_ID, size=500, max_pages=1)
  assert result['total'] == 1
  assert result['size'] == 500
  assert result['page'] == 0
  assert len(result['collection']) == 1


def test_get_instance(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=INSTANCE_RESPONSE)
  result = api.get_instance(INSTANCE_ID)
  assert result == INSTANCE_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_INSTANCE(INSTANCE_ID))
  _assert_validates_schema(result, INSTANCE_SCHEMA)


def test_get_sector(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=SECTOR_RESPONSE)
  result = api.get_sector(SECTOR_ID)
  assert result == SECTOR_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_SECTOR(SECTOR_ID))
  _assert_validates_schema(result, SECTOR_SCHEMA)


def test_get_vaccines(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=GLOBAL_VACCINES_PAGE)
  result = api.get_vaccines()
  assert result == GLOBAL_VACCINES_PAGE
  assert_get_called(mock_get, MICROCLAUDIA_VACCINES(50))
  _assert_validates_schema(result, VACCINES_SCHEMA)


def test_get_agent(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=AGENT_RESPONSE)
  result = api.get_agent(AGENT_ID)
  assert result == AGENT_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_AGENT_CONTENT(AGENT_ID))
  _assert_validates_schema(result, AGENT_SCHEMA)


def test_get_agents_from_agency_with_default_filter(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=AGENTS_PAGE)
  result = api.get_agents_from_agency(
      AGENCY_ID, size=50, page=0, filter_by='osFamily:linux',
  )
  assert result == AGENTS_PAGE
  assert_get_called(
      mock_get,
      add_query_params(
          MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 50, 0),
          defaultFilter='osFamily:linux',
      ),
  )


def test_get_deployments_sector_stats(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=DEPLOYMENTS_SECTOR_STATS_RESPONSE)
  result = api.get_deployments_sector_stats()
  assert result == DEPLOYMENTS_SECTOR_STATS_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_DEPLOYMENTS_SECTOR_STATS(5))
  _assert_validates_schema(result, STATS_COUNT_SCHEMA)


def _mock_requests_response(json_data=None, status_code=HTTPStatus.OK):
  response = MagicMock()
  response.status_code = status_code
  response.ok = status_code < 400
  response.content = json.dumps(json_data or {'ok': True}).encode('utf-8')
  response.text = response.content.decode('utf-8')
  return response


AGENT_ID_2 = 'b' * 64

_AUTH_HEADER = {'authorization': 'Bearer test-token'}


def _agent_with_tags(tags):
  return {**AGENT_RESPONSE, 'tags': tags}


def test_get_tags_from_agency(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=TAGS_PAGE)
  result = api.get_tags_from_agency(AGENCY_ID)
  assert result == TAGS_PAGE
  assert_get_called(mock_get, MICROCLAUDIA_AGENCY_TAGS_CONTENT(AGENCY_ID))


def test_get_tags_from_agent(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=_agent_with_tags(['t1', 't2']))
  result = api.get_tags_from_agent(AGENT_ID)
  assert result == ['t1', 't2']
  assert_get_called(mock_get, MICROCLAUDIA_AGENT_CONTENT(AGENT_ID))


def test_get_tags_from_agent_defaults_to_empty(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data={'id': AGENT_ID})
  assert api.get_tags_from_agent(AGENT_ID) == []


def test_get_tags_from_agents(api, mock_get):
  mock_get.side_effect = [
      MockHttpResponse(json_data=_agent_with_tags(['t1'])),
      MockHttpResponse(json_data=_agent_with_tags(['t2', 't3'])),
  ]
  result = api.get_tags_from_agents([AGENT_ID, AGENT_ID_2])
  assert result == {AGENT_ID: ['t1'], AGENT_ID_2: ['t2', 't3']}


def test_set_tags_to_agent(api, mock_requests):
  mock_requests.return_value = _mock_requests_response(_agent_with_tags(['t1']))
  result = api.set_tags_to_agent(AGENT_ID, tags=['t1'])
  assert result == ['t1']
  mock_requests.assert_called_once_with(
      MICROCLAUDIA_AGENT_CONTENT(AGENT_ID),
      headers=_AUTH_HEADER,
      json={'tags': ['t1']},
      timeout=MICROCLAUDIA_REQUEST_TIMEOUT,
  )


def test_set_tags_to_agents(api, mock_requests):
  mock_requests.side_effect = [
      _mock_requests_response(_agent_with_tags(['t1'])),
      _mock_requests_response(_agent_with_tags(['t1'])),
  ]
  result = api.set_tags_to_agents([AGENT_ID, AGENT_ID_2], tags=['t1'])
  assert result == {AGENT_ID: ['t1'], AGENT_ID_2: ['t1']}
  assert mock_requests.call_count == 2


def test_add_tags_to_agent_merges_existing(api, mock_get, mock_requests):
  mock_get.return_value = MockHttpResponse(json_data=_agent_with_tags(['existing']))
  mock_requests.return_value = _mock_requests_response(_agent_with_tags(['existing', 'new']))
  result = api.add_tags_to_agent(AGENT_ID, tags=['new'])
  assert result == ['existing', 'new']
  mock_requests.assert_called_once_with(
      MICROCLAUDIA_AGENT_CONTENT(AGENT_ID),
      headers=_AUTH_HEADER,
      json={'tags': ['existing', 'new']},
      timeout=MICROCLAUDIA_REQUEST_TIMEOUT,
  )


def test_add_tags_to_agents(api, mocker):
  mock_add = mocker.patch.object(api, 'add_tags_to_agent', side_effect=[['new'], ['new']])
  result = api.add_tags_to_agents([AGENT_ID, AGENT_ID_2], tags=['new'])
  assert result == {AGENT_ID: ['new'], AGENT_ID_2: ['new']}
  assert mock_add.call_count == 2


def test_remove_tags_from_agent(api, mock_get, mock_requests):
  mock_get.return_value = MockHttpResponse(json_data=_agent_with_tags(['t1', 't2']))
  mock_requests.return_value = _mock_requests_response(_agent_with_tags(['t2']))
  result = api.remove_tags_from_agent(AGENT_ID, tags=['t1'])
  assert result == ['t2']
  mock_requests.assert_called_once_with(
      MICROCLAUDIA_AGENT_CONTENT(AGENT_ID),
      headers=_AUTH_HEADER,
      json={'tags': ['t2']},
      timeout=MICROCLAUDIA_REQUEST_TIMEOUT,
  )


def test_remove_tags_from_agents(api, mocker):
  mock_remove = mocker.patch.object(api, 'remove_tags_from_agent', side_effect=[['t2'], []])
  result = api.remove_tags_from_agents([AGENT_ID, AGENT_ID_2], tags=['t1'])
  assert result == {AGENT_ID: ['t2'], AGENT_ID_2: []}
  assert mock_remove.call_count == 2


def test_clear_tags_from_agent(api, mock_requests):
  mock_requests.return_value = _mock_requests_response(_agent_with_tags([]))
  result = api.clear_tags_from_agent(AGENT_ID)
  assert result == []
  mock_requests.assert_called_once_with(
      MICROCLAUDIA_AGENT_CONTENT(AGENT_ID),
      headers=_AUTH_HEADER,
      json={'tags': []},
      timeout=MICROCLAUDIA_REQUEST_TIMEOUT,
  )


def test_clear_tags_from_agents(api, mocker):
  mock_clear = mocker.patch.object(api, 'clear_tags_from_agent', side_effect=[[], []])
  result = api.clear_tags_from_agents([AGENT_ID, AGENT_ID_2])
  assert result == {AGENT_ID: [], AGENT_ID_2: []}
  assert mock_clear.call_count == 2


def test_unauthorized_retries_refresh_and_calls_get_twice(api, mock_get, mock_post):
  """On 401, refresh token first then retry the request once."""
  instances_body = [{'id': INSTANCE_ID}]
  mock_post.side_effect = [
      MockHttpResponse(
          headers={
              'Authorization': 'Bearer refreshed-access-token',
              'refresh-token': 'Bearer refreshed-refresh-token',
          },
      ),
  ]
  mock_get.side_effect = [
      MockHttpResponse(status_code=HTTPStatus.UNAUTHORIZED),
      MockHttpResponse(json_data=instances_body),
  ]
  result = api.get_instances()
  assert result == instances_body
  assert mock_get.call_count == 2
  assert mock_post.call_count == 2  # __init__ login + refresh on 401
  assert mock_post.call_args_list[1][0][0] == MICROCLAUDIA_AUTH_REFRESH
  assert api.authorization_token == 'Bearer refreshed-access-token'
  assert api.refresh_token == 'Bearer refreshed-refresh-token'


def test_unauthorized_falls_back_to_login_when_refresh_fails(api, mock_get, mock_post):
  instances_body = [{'id': INSTANCE_ID}]
  mock_post.side_effect = [
      MockHttpResponse(status_code=HTTPStatus.UNAUTHORIZED),
      MockHttpResponse(
          headers={
              'Authorization': 'Bearer relogin-access-token',
              'refresh-token': 'Bearer relogin-refresh-token',
          },
      ),
  ]
  mock_get.side_effect = [
      MockHttpResponse(status_code=HTTPStatus.UNAUTHORIZED),
      MockHttpResponse(json_data=instances_body),
  ]
  result = api.get_instances()
  assert result == instances_body
  assert mock_get.call_count == 2
  assert mock_post.call_count == 3  # __init__ login + failed refresh + relogin
  assert mock_post.call_args_list[1][0][0] == MICROCLAUDIA_AUTH_REFRESH
  assert mock_post.call_args_list[2][0][0].endswith('/login')


def test_unauthorized_raises_after_second_401(api, mock_get, mock_post):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaAuthError

  login_headers = {
      'Authorization': 'Bearer initial-access-token',
      'refresh-token': 'refresh-token-value',
  }
  mock_post.side_effect = [
      MockHttpResponse(headers=login_headers),
      MockHttpResponse(
          headers={
              'Authorization': 'Bearer refreshed-access-token',
              'refresh-token': 'Bearer refreshed-refresh-token',
          },
      ),
  ]
  mock_get.side_effect = [
      MockHttpResponse(status_code=HTTPStatus.UNAUTHORIZED),
      MockHttpResponse(status_code=HTTPStatus.UNAUTHORIZED),
  ]
  with pytest.raises(MicroClaudiaAuthError, match='still unauthorized'):
    api.get_instances()
  assert mock_get.call_count == 2


def test_forbidden_raises_without_retry(api, mock_get, mock_post):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaForbiddenError

  mock_get.return_value = MockHttpResponse(status_code=HTTPStatus.FORBIDDEN)
  with pytest.raises(MicroClaudiaForbiddenError):
    api.get_sectors()
  assert mock_get.call_count == 1
  assert mock_post.call_count == 1


def test_not_found_raises_api_error(api, mock_get):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaAPIError

  mock_get.return_value = MockHttpResponse(
      status_code=HTTPStatus.NOT_FOUND,
      text='{"error":"not found"}',
  )
  with pytest.raises(MicroClaudiaAPIError) as exc_info:
    api.get_instances()
  assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
  assert mock_get.call_count == 1


def test_server_error_raises_api_error(api, mock_get):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaAPIError

  mock_get.return_value = MockHttpResponse(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
  with pytest.raises(MicroClaudiaAPIError) as exc_info:
    api.get_instances()
  assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
  assert mock_get.call_count == 1


def test_rate_limit_raises_rate_limit_error(api, mock_get):
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaRateLimitError

  mock_get.return_value = MockHttpResponse(status_code=HTTPStatus.TOO_MANY_REQUESTS)
  with pytest.raises(MicroClaudiaRateLimitError) as exc_info:
    api.get_instances()
  assert exc_info.value.status_code == HTTPStatus.TOO_MANY_REQUESTS
  assert mock_get.call_count == 1


def test_authorized_get_passes_default_timeout(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=[{'id': INSTANCE_ID}])
  api.get_instances()
  assert mock_get.call_args.kwargs['timeout'] == MICROCLAUDIA_REQUEST_TIMEOUT


def test_authorized_get_honors_caller_timeout_override(api, mock_get):
  api._authorized_get(MICROCLAUDIA_INSTANCE_LIST, timeout=120)
  assert mock_get.call_args.kwargs['timeout'] == 120


def test_authorized_get_raises_timeout_error(api, mock_get):
  import requests

  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaTimeoutError
  from microclaudia_api.core.static.microclaudia_uri_constants import MICROCLAUDIA_INSTANCE_LIST

  mock_get.side_effect = requests.Timeout('timed out')
  with pytest.raises(MicroClaudiaTimeoutError) as exc_info:
    api.get_instances()
  assert exc_info.value.url == MICROCLAUDIA_INSTANCE_LIST


def test_login_raises_timeout_error(mock_post):
  import requests

  from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI
  from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaTimeoutError
  from microclaudia_api.core.static.microclaudia_uri_constants import MICROCLAUDIA_LOGIN

  mock_post.side_effect = requests.Timeout('timed out')
  api = MicroClaudiaAPI.__new__(MicroClaudiaAPI)
  api.username = 'user'
  api.password = 'pass'
  with pytest.raises(MicroClaudiaTimeoutError) as exc_info:
    api.login('user', 'pass')
  assert exc_info.value.url == MICROCLAUDIA_LOGIN


def test_reauthenticate_updates_both_tokens(api, mock_post):
  api.refresh_token = REFRESH_TOKEN_HEADER
  mock_post.return_value = MockHttpResponse(
      headers={
          'Authorization': 'Bearer new-access-token',
          'refresh-token': 'Bearer new-refresh-token',
      },
  )
  api._reauthenticate()
  assert api.authorization_token == 'Bearer new-access-token'
  assert api.refresh_token == 'Bearer new-refresh-token'
  assert mock_post.call_args[0][0] == MICROCLAUDIA_AUTH_REFRESH


def test_get_agencies_from_sectors_calls_sector_agencies_url(api, mock_get):
  body = PAGINATED_EMPTY
  mock_get.return_value = MockHttpResponse(json_data=body)
  result = api.get_agencies_from_sector(SECTOR_ID, size=10, page=0)
  assert result == body
  assert_get_called(mock_get, MICROCLAUDIA_SECTOR_AGENCIES_CONTENT(SECTOR_ID, 10, 0))


def test_get_version(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=VERSION_RESPONSE)
  result = api.get_version()
  assert result == VERSION_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_VERSION)
  _assert_validates_schema(result, VERSION_SCHEMA)


def test_get_oses(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=OSES_RESPONSE)
  result = api.get_oses()
  assert result == OSES_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_OSES)
  _assert_validates_schema(result, OSES_SCHEMA)


def test_get_users(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=USERS_PAGE)
  result = api.get_users()
  assert result == USERS_PAGE
  assert_get_called(mock_get, MICROCLAUDIA_USERS(50))
  _assert_validates_schema(result, USERS_SCHEMA)


def test_get_user_roles(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=USER_ROLES_RESPONSE)
  result = api.get_user_roles()
  assert result == USER_ROLES_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_USER_ROLES)
  _assert_validates_schema(result, USER_ROLES_SCHEMA)


def test_get_stats_news(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=STATS_NEWS_RESPONSE)
  result = api.get_stats_news()
  assert result == STATS_NEWS_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_STATS_NEWS)
  _assert_validates_schema(result, STATS_NEWS_SCHEMA)


def test_get_agents_last_version(api, mock_get):
  mock_get.return_value = MockHttpResponse(json_data=AGENTS_LAST_VERSION_RESPONSE)
  result = api.get_agents_last_version()
  assert result == AGENTS_LAST_VERSION_RESPONSE
  assert_get_called(mock_get, MICROCLAUDIA_AGENTS_LAST_VERSION)
  _assert_validates_schema(result, AGENTS_LAST_VERSION_SCHEMA)


def test_auth_refresh(api, mock_post):
  api.refresh_token = REFRESH_TOKEN_HEADER
  mock_post.return_value = MockHttpResponse(
      json_data=AUTH_REFRESH_RESPONSE,
      headers={
          'Authorization': 'Bearer new-access-token',
          'refresh-token': 'Bearer new-refresh-token',
      },
  )
  result = api.auth_refresh()
  assert result == AUTH_REFRESH_RESPONSE
  assert api.authorization_token == 'Bearer new-access-token'
  assert api.refresh_token == 'Bearer new-refresh-token'
  call = mock_post.call_args
  assert call[0][0] == MICROCLAUDIA_AUTH_REFRESH
  assert call[1]['json'] == {'refreshToken': REFRESH_TOKEN_HEADER}
  _assert_validates_schema(result, AUTH_REFRESH_SCHEMA)


def test_auth_refresh_logs_in_when_refresh_token_missing(api, mock_post):
  api.refresh_token = None
  mock_post.return_value = MockHttpResponse(
      json_data=AUTH_REFRESH_RESPONSE,
      headers={
          'Authorization': 'Bearer new-access-token',
          'refresh-token': 'Bearer new-refresh-token',
      },
  )
  api.auth_refresh()
  assert mock_post.call_count >= 2
  assert mock_post.call_args_list[-1][0][0] == MICROCLAUDIA_AUTH_REFRESH


 
