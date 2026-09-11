# -*- coding: utf-8 -*-
"""Helpers for live MicroClaudia API method probes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Optional

from microclaudia_api.core.static.microclaudia_exceptions import (
    MicroClaudiaAPIError,
    MicroClaudiaAuthError,
    MicroClaudiaForbiddenError,
    MicroClaudiaRateLimitError,
    MicroClaudiaSchemaError,
    MicroClaudiaTimeoutError,
)


@dataclass
class LiveCallOutcome:
  method: str
  status: str  # ok | empty_body | forbidden | rate_limited | error | not_implemented | wrapper_bug
  result: Any = None
  detail: str = ''


def probe(method_name: str, call: Callable[[], Any]) -> LiveCallOutcome:
  try:
    result = call()
    if result is None and method_name == 'get_all_agents_stats_from_agency':
      return LiveCallOutcome(
          method_name, 'wrapper_bug', result,
          'Method completed but returned None (likely wrapper bug).',
      )
    return LiveCallOutcome(method_name, 'ok', result)
  except TypeError as exc:
    if 'NotImplemented' in str(exc) or 'exceptions must derive' in str(exc):
      return LiveCallOutcome(method_name, 'not_implemented', detail=str(exc))
    return LiveCallOutcome(method_name, 'error', detail=str(exc))
  except json.JSONDecodeError as exc:
    return LiveCallOutcome(
        method_name, 'empty_body', detail=f'Non-JSON/empty response: {exc}',
    )
  except MicroClaudiaForbiddenError as exc:
    return LiveCallOutcome(method_name, 'forbidden', detail=str(exc))
  except MicroClaudiaRateLimitError as exc:
    return LiveCallOutcome(method_name, 'rate_limited', detail=str(exc))
  except MicroClaudiaAPIError as exc:
    return LiveCallOutcome(method_name, 'error', detail=str(exc))
  except MicroClaudiaSchemaError as exc:
    return LiveCallOutcome(method_name, 'error', detail=str(exc))
  except MicroClaudiaTimeoutError as exc:
    return LiveCallOutcome(method_name, 'error', detail=str(exc))
  except MicroClaudiaAuthError as exc:
    return LiveCallOutcome(method_name, 'error', detail=str(exc))
  except Exception as exc:
    return LiveCallOutcome(method_name, 'error', detail=f'{type(exc).__name__}: {exc}')


def assert_ok(outcome: LiveCallOutcome, *, allow_none: bool = False, skip_transient: bool = False):
  if outcome.status == 'ok' and (allow_none or outcome.result is not None):
    return
  if outcome.status in ('empty_body', 'forbidden', 'rate_limited'):
    if skip_transient:
      import pytest
      pytest.skip(f'{outcome.method}: transient API error or rate limit — {outcome.detail}')
    raise AssertionError(
        f'{outcome.method}: API returned empty/non-JSON body or forbidden. {outcome.detail}'
    )
  if outcome.status == 'wrapper_bug':
    raise AssertionError(f'{outcome.method}: {outcome.detail}')
  if outcome.status == 'not_implemented':
    raise AssertionError(f'{outcome.method}: not implemented ({outcome.detail})')
  raise AssertionError(f'{outcome.method}: {outcome.status} — {outcome.detail}')


def assert_list_payload(outcome: LiveCallOutcome, *, min_len: int = 1, skip_transient: bool = False):
  assert_ok(outcome, skip_transient=skip_transient)
  assert isinstance(outcome.result, list), f'{outcome.method}: expected list, got {type(outcome.result)}'
  assert len(outcome.result) >= min_len, f'{outcome.method}: expected >={min_len} items'


def assert_dict_payload(outcome: LiveCallOutcome, *, keys: Optional[tuple] = None):
  assert_ok(outcome)
  assert isinstance(outcome.result, dict), f'{outcome.method}: expected dict, got {type(outcome.result)}'
  if keys:
    missing = [k for k in keys if k not in outcome.result]
    assert not missing, f'{outcome.method}: missing keys {missing}'
