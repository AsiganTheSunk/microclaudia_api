# -*- coding: utf-8 -*-
"""Ensure fixture payloads satisfy the JSON schemas used in production."""

from jsonschema import validate

from microclaudia_api.core.static.schemas.microclaudia_schemas import (
    AGENTS_FROM_AGENCY_SCHEMA,
    ALERTS_FROM_AGENCY_SCHEMA,
    CSV_AGENTS_SCHEMA,
    INSTANCES_RESPONSE_SCHEMA,
    PREPARE_CSV_TASK_SCHEMA,
    TOTAL_STATS_FORM_EVOLUTION_SCHEMA,
    TOTAL_STATS_SCHEMA,
)
import json
from csv import DictReader
from json import dumps

from tests.fixtures.sample_data import (
    AGENTS_PAGE,
    ALERTS_PAGE,
    CSV_ROW,
    EVOLUTION_STATS,
    INSTANCE_ID,
    TOTAL_STATS,
)


def test_agents_page_matches_v2_schema():
  validate(instance=AGENTS_PAGE, schema=AGENTS_FROM_AGENCY_SCHEMA)


def test_alerts_page_matches_schema():
  validate(instance=ALERTS_PAGE, schema=ALERTS_FROM_AGENCY_SCHEMA)


def test_csv_fixture_matches_schema():
  contents = dumps(list(DictReader(CSV_ROW.splitlines(), delimiter=';')), indent=4)
  validate(instance=json.loads(contents), schema=CSV_AGENTS_SCHEMA)


def test_total_stats_fixture_matches_schema():
  validate(instance=TOTAL_STATS, schema=TOTAL_STATS_SCHEMA)


def test_evolution_stats_fixture_matches_schema():
  validate(instance=EVOLUTION_STATS, schema=TOTAL_STATS_FORM_EVOLUTION_SCHEMA)


def test_instances_list_fixture_matches_response_schema():
  validate(instance=[{'id': INSTANCE_ID}], schema=INSTANCES_RESPONSE_SCHEMA)


def test_prepare_csv_task_fixture_matches_schema():
  validate(instance={'task': 'created'}, schema=PREPARE_CSV_TASK_SCHEMA)
