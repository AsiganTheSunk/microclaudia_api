# -*- coding: utf-8 -*-
"""Regression test: 401 retry preserves decorator behavior with kwargs."""

from http import HTTPStatus

import pytest

from tests.conftest import MockHttpResponse
from tests.fixtures.sample_data import AGENCY_ID, TAGS_PAGE


def test_unauthorized_retry_with_kwargs_breaks_decorated_method(api, mock_get):
  mock_get.side_effect = [
      MockHttpResponse(status_code=HTTPStatus.UNAUTHORIZED),
      MockHttpResponse(json_data=TAGS_PAGE),
  ]
  result = api.get_tags_from_agency(agency_id=AGENCY_ID)
  assert result == TAGS_PAGE
