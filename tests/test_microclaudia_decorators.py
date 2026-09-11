# -*- coding: utf-8 -*-

import pytest

from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI
from microclaudia_api.core.static.microclaudia_exceptions import (
    MicroClaudiaAgencyError,
    MicroClaudiaInstanceError,
    MicroClaudiaPatternError,
    MicroClaudiaSectorError,
)
from tests.fixtures.sample_data import AGENCY_ID, INSTANCE_ID, SECTOR_ID


@pytest.fixture
def api_no_login(mock_get, mock_post, mock_sleep):
  client = MicroClaudiaAPI.__new__(MicroClaudiaAPI)
  client.authorization_token = 'Bearer test-token'
  client.username = 'u'
  client.password = 'p'
  return client


def test_require_agency_id_rejects_none(api_no_login):
  with pytest.raises(MicroClaudiaAgencyError):
    api_no_login.get_agents_from_agency(None)


def test_require_agency_id_rejects_invalid_pattern(api_no_login):
  with pytest.raises(MicroClaudiaPatternError):
    api_no_login.get_agents_from_agency('not-a-valid-id')


def test_require_instance_id_rejects_none(api_no_login):
  with pytest.raises(MicroClaudiaInstanceError):
    api_no_login.get_sectors_from_instance(None)


def test_require_sector_id_rejects_none(api_no_login):
  with pytest.raises(MicroClaudiaSectorError):
    api_no_login.get_agencies_from_sector(None)


def test_valid_agency_id_passes_decorators(api_no_login, mock_get):
  from tests.conftest import MockHttpResponse

  mock_get.return_value = MockHttpResponse(json_data={'tags': []})
  api_no_login.get_tags_from_agency(AGENCY_ID)


def test_valid_instance_id_passes_decorators(api_no_login, mock_get):
  from tests.conftest import MockHttpResponse
  from tests.fixtures.sample_data import PAGINATED_EMPTY

  mock_get.return_value = MockHttpResponse(json_data=PAGINATED_EMPTY)
  api_no_login.get_sectors_from_instance(INSTANCE_ID, size=1, page=0)


def test_valid_sector_id_passes_decorators(api_no_login, mock_get):
  from tests.conftest import MockHttpResponse
  from tests.fixtures.sample_data import PAGINATED_EMPTY

  mock_get.return_value = MockHttpResponse(json_data=PAGINATED_EMPTY)
  api_no_login.get_agencies_from_sector(SECTOR_ID, size=1, page=0)
