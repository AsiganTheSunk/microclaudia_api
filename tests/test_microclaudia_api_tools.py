# -*- coding: utf-8 -*-

import pytest

from microclaudia_api.core.microclaudia_api_tools import (
    add_query_params,
    filter_agents,
    order_agents,
    sort_agents,
)
from microclaudia_api.core.static.microclaudia_uri_constants import (
    MICROCLAUDIA_AGENCY_AGENT_CONTENT,
)
from tests.fixtures.sample_data import AGENCY_ID


@pytest.mark.parametrize(
    'url,params,expected',
    [
        (
            'https://example/api/stats',
            {'groupBy': 'os family', 'size': 50, 'page': 0},
            'https://example/api/stats?groupBy=os+family&size=50&page=0',
        ),
        (
            'https://example/api/stats?size=50',
            {'page': 0, 'filter': None},
            'https://example/api/stats?size=50&page=0',
        ),
        ('https://example/api/stats', {'page': None}, 'https://example/api/stats'),
    ],
)
def test_add_query_params(url, params, expected):
  assert add_query_params(url, **params) == expected


@pytest.mark.parametrize(
    'sort_by,expected_fragment',
    [
        ('info.computer_name', 'sortBy=info.computer_name'),
        ('computerName', 'sortBy=computerName'),
        ('version', 'sortBy=version'),
        (None, None),
        ('invalid', None),
    ],
)
def test_sort_agents(sort_by, expected_fragment):
  base = MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 50, 0)
  url = sort_agents(base, sort_by)
  if expected_fragment:
    assert expected_fragment in url
  else:
    assert url == base


@pytest.mark.parametrize(
    'order_by,expected_fragment',
    [
        ('asc', 'orderBy=asc'),
        ('desc', 'orderBy=desc'),
        ('invalid', None),
    ],
)
def test_order_agents(order_by, expected_fragment):
  base = MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 50, 0)
  url = order_agents(base, order_by)
  if expected_fragment:
    assert expected_fragment in url
  else:
    assert url == base


def test_filter_agents_tag():
  base = MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 50, 0)
  url = filter_agents(base, 'ciberseguridad')
  assert url.endswith('&filter=ciberseguridad')


def test_filter_agents_uses_first_tag(capsys):
  base = MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 50, 0)
  assert filter_agents(base, ['primary', 'ignored']).endswith('&filter=primary')
  assert 'only the main tag will be applied' in capsys.readouterr().out


def test_filter_agents_ignores_empty_tag_list():
  base = MICROCLAUDIA_AGENCY_AGENT_CONTENT(AGENCY_ID, 50, 0)
  assert filter_agents(base, []) == base
