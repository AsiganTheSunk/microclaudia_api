# -*- coding: utf-8 -*-
"""Live test configuration and runtime discovery helpers."""

from __future__ import annotations

import os
import sys
from getpass import getpass

LIVE_AGENCY_EQUIPS = os.environ.get('MICROCLAUDIA_LIVE_AGENCY_EQUIPS')
LIVE_AGENCY_SERVERS = os.environ.get('MICROCLAUDIA_LIVE_AGENCY_SERVERS')

_CREDENTIALS_HELP = (
    'Live credentials required. Set MICROCLAUDIA_LIVE_USERNAME / '
    'MICROCLAUDIA_LIVE_PASSWORD (or, for pytest only, --live-user / --live-password). '
    'Interactive prompt needs a real terminal.'
)


def resolve_live_credentials(
    username: str | None = None,
    password: str | None = None,
    *,
    allow_prompt: bool = True,
) -> tuple[str, str]:
    """
    Resolve live credentials from (in order): explicit args, env, interactive prompt.
    Env: MICROCLAUDIA_LIVE_USERNAME, MICROCLAUDIA_LIVE_PASSWORD
    """
    user = (username or os.environ.get('MICROCLAUDIA_LIVE_USERNAME') or '').strip()
    pwd = password or os.environ.get('MICROCLAUDIA_LIVE_PASSWORD') or ''
    if (not user or not pwd) and allow_prompt:
        try:
            if not user:
                print('MICROCLAUDIA_LIVE_USERNAME: ', end='', file=sys.__stderr__, flush=True)
                user = (sys.__stdin__ or sys.stdin).readline().strip()
            if not pwd:
                pwd = getpass('MICROCLAUDIA_LIVE_PASSWORD: ', stream=sys.__stderr__)
        except (EOFError, OSError) as error:
            raise RuntimeError(_CREDENTIALS_HELP) from error
    if not user or not pwd:
        raise RuntimeError(_CREDENTIALS_HELP)
    return user, pwd


def _iter_collection(payload):
    if isinstance(payload, dict):
        collection = payload.get('collection')
        if isinstance(collection, list):
            return collection
    if isinstance(payload, list):
        return payload
    return []


def discover_live_context(api) -> dict[str, str | None]:
    """
    Discover usable live IDs from the authenticated account.

    Env overrides still win, but there are no hardcoded defaults.
    """
    ctx = {
        'agency_id': LIVE_AGENCY_EQUIPS,
        'agency_servers': LIVE_AGENCY_SERVERS,
        'instance_id': None,
        'sector_id': None,
    }

    try:
        alerts = api.get_alerts(size=10, page=0)
    except Exception:
        alerts = None
    for item in _iter_collection(alerts):
        agency = item.get('agency') or {}
        ctx['agency_id'] = ctx['agency_id'] or agency.get('id')
        ctx['agency_servers'] = ctx['agency_servers'] or agency.get('id')
        ctx['instance_id'] = ctx['instance_id'] or agency.get('instanceId')
        ctx['sector_id'] = ctx['sector_id'] or agency.get('sector')
        if ctx['agency_id'] and ctx['instance_id'] and ctx['sector_id']:
            return ctx

    try:
        sectors = api.get_sectors()
    except Exception:
        sectors = None
    for item in _iter_collection(sectors):
        ctx['sector_id'] = ctx['sector_id'] or item.get('id')
        ctx['instance_id'] = ctx['instance_id'] or item.get('instanceId')
        if ctx['sector_id']:
            try:
                agencies = api.get_agencies_from_sector(ctx['sector_id'], size=10, page=0)
            except Exception:
                agencies = None
            agency_items = _iter_collection(agencies)
            if agency_items:
                agency_id = agency_items[0].get('id')
                ctx['agency_id'] = ctx['agency_id'] or agency_id
                ctx['agency_servers'] = ctx['agency_servers'] or agency_id
                return ctx

    try:
        instances = api.get_instances(size=10)
    except Exception:
        instances = None
    for item in _iter_collection(instances):
        ctx['instance_id'] = ctx['instance_id'] or item.get('id')
        if ctx['instance_id']:
            try:
                agencies = api.get_agencies_from_instance(ctx['instance_id'], size=10)
            except Exception:
                agencies = None
            agency_items = _iter_collection(agencies)
            if agency_items:
                agency_id = agency_items[0].get('id')
                ctx['agency_id'] = ctx['agency_id'] or agency_id
                ctx['agency_servers'] = ctx['agency_servers'] or agency_id
                return ctx

    return ctx
