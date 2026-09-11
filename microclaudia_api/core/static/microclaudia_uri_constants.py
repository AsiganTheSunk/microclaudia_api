#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: Typing Module Imports
from typing import Callable, Tuple

from microclaudia_api.core.microclaudia_api_tools import add_query_params


MICROCLAUDIA_REQUEST_TIMEOUT: Tuple[int, int] = (10, 30)

# Note: milliseconds on Windows, converted to seconds for the unix ping -w flag.
MICROCLAUDIA_PING_TIMEOUT: int = 10000

MICROCLAUDIA_BASE_DOMAIN: str = f'microclaudia.ccn-cert.cni.es'

MICROCLAUDIA_URL: str = f'https://{MICROCLAUDIA_BASE_DOMAIN}'

MICROCLAUDIA_API_URL: str = f'{MICROCLAUDIA_URL}/api'

MICROCLAUDIA_LOGIN: str = f'{MICROCLAUDIA_API_URL}/login'

# Note: ---------------------------------------------------------------------------------------------------------------

MICROCLAUDIA_INSTANCE_LIST: str = f'{MICROCLAUDIA_API_URL}/instances'

MICROCLAUDIA_INSTANCE: Callable[[str], str] = \
    lambda agency_id: \
    f'{MICROCLAUDIA_API_URL}/instances/{agency_id}'

MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA: Callable[[str, str, str, int, int], str] = \
    lambda agency_id, section, content, size=10, page=0: \
    add_query_params(
        f'{MICROCLAUDIA_AGENCY(agency_id=agency_id)}/stats/{section}/count',
        groupBy=content, size=size, page=page
    )

MICROCLAUDIA_AGENCIES_FROM_INSTANCE: Callable[[str, int], str] = \
    lambda instance_id, size=200: \
    add_query_params(f'{MICROCLAUDIA_INSTANCE(agency_id=instance_id)}/agencies/all', size=size)

MICROCLAUDIA_INSTANCE_CONTENT: Callable[[str, str, int, int], str] = \
    lambda agency_id, agency_content, size=10, page=0: \
    add_query_params(
        f'{MICROCLAUDIA_INSTANCE(agency_id=agency_id)}/{agency_content}',
        size=size, page=page
    )

MICROCLAUDIA_INSTANCE_SECTOR_CONTENT: Callable[[str, int, int], str] = \
    lambda agency_id, size=10, page=0: \
    MICROCLAUDIA_INSTANCE_CONTENT(agency_id, 'sectors', size, page)

MICROCLAUDIA_AGENCY_STATS_CONTENT: Callable[[str, str, int, int], str] = \
    lambda section, content, size=10, page=0: \
    add_query_params(
        f'{MICROCLAUDIA_API_URL}/stats/{section}/count',
        groupBy=content, size=size, page=page
    )

MICROCLAUDIA_TOTAL_STATS: str = \
    f'{MICROCLAUDIA_API_URL}/stats/totals'

MICROCLAUDIA_STATS_EVOLUTION: Callable[[int], str] = \
    lambda evolution_id=7: \
    f'{MICROCLAUDIA_API_URL}/stats/evolution/{evolution_id}'

MICROCLAUDIA_ALERTS: Callable[[int, int], str] = \
    lambda size=10, page=0: \
    add_query_params(f'{MICROCLAUDIA_API_URL}/alerts', size=size, page=page)

# Note: ---------------------------------------------------------------------------------------------------------------

MICROCLAUDIA_SECTOR_LIST: str = f'{MICROCLAUDIA_API_URL}/sectors'

MICROCLAUDIA_SECTOR: Callable[[str], str] = \
    lambda agency_id: \
    f'{MICROCLAUDIA_API_URL}/sectors/{agency_id}'

MICROCLAUDIA_SECTOR_AGENCIES_CONTENT: Callable[[str, int, int], str] = \
    lambda sector_id, size=10, page=0: \
    add_query_params(f'{MICROCLAUDIA_API_URL}/sectors/{sector_id}/agencies', size=size, page=page)

MICROCLAUDIA_AGENT_CONTENT: Callable[[str], str] = \
    lambda agent_id: \
    f'{MICROCLAUDIA_API_URL}/agents/{agent_id}'

# Note: ---------------------------------------------------------------------------------------------------------------

MICROCLAUDIA_AGENCY: Callable[[str], str] = \
    lambda agency_id: \
    f'{MICROCLAUDIA_API_URL}/agencies/{agency_id}'

MICROCLAUDIA_AGENCY_CONTENT: Callable[[str, str, int, int], str] = \
    lambda agency_id, agency_content, size=10, page=0: \
    add_query_params(
        f'{MICROCLAUDIA_AGENCY(agency_id=agency_id)}/{agency_content}',
        size=size, page=page
    )

MICROCLAUDIA_AGENCY_AGENT_CONTENT: Callable[[str, int, int], str] = \
    lambda agency_id, size=10, page=0: \
    MICROCLAUDIA_AGENCY_CONTENT(agency_id, 'agents', size, page)

MICROCLAUDIA_AGENCY_ALERTS_CONTENT: Callable[[str, int, int], str] = \
    lambda agency_id, size=10, page=0: \
    MICROCLAUDIA_AGENCY_CONTENT(agency_id, 'alerts', size, page)

MICROCLAUDIA_AGENCY_VACCINE_CONTENT: Callable[[str, int, int], str] = \
    lambda agency_id, size=10, page=0: \
    MICROCLAUDIA_AGENCY_CONTENT(agency_id, 'vaccines', size, page)

MICROCLAUDIA_AGENCY_TAGS_CONTENT: Callable[[str, int, int], str] = \
    lambda agency_id, size=10, page=0: \
    MICROCLAUDIA_AGENCY_CONTENT(agency_id, 'tags', size, page)

# Note: ---------------------------------------------------------------------------------------------------------------

MICROCLAUDIA_ALERTS_CSV: str = f'{MICROCLAUDIA_API_URL}/alerts/preparecsv'

MICROCLAUDIA_TASKS: str = f'{MICROCLAUDIA_API_URL}/tasks'

MICROCLAUDIA_TASK: Callable[[str], str] = \
    lambda task_id: \
    f'{MICROCLAUDIA_TASKS}/{task_id}'

# Note: ---------------------------------------------------------------------------------------------------------------

MICROCLAUDIA_VERSION: str = f'{MICROCLAUDIA_API_URL}/version'

MICROCLAUDIA_OSES: str = f'{MICROCLAUDIA_API_URL}/oses'

MICROCLAUDIA_USERS: Callable[[int], str] = \
    lambda size=50: \
    add_query_params(f'{MICROCLAUDIA_API_URL}/users', size=size)

MICROCLAUDIA_USER_ROLES: str = f'{MICROCLAUDIA_API_URL}/users/roles'

MICROCLAUDIA_STATS_NEWS: str = f'{MICROCLAUDIA_API_URL}/stats/news'

MICROCLAUDIA_AUTH_REFRESH: str = f'{MICROCLAUDIA_API_URL}/auth/refresh'

MICROCLAUDIA_AGENTS_LAST_VERSION: str = f'{MICROCLAUDIA_API_URL}/agents/lastVersion'

MICROCLAUDIA_VACCINES: Callable[[int], str] = \
    lambda size=50: \
    add_query_params(f'{MICROCLAUDIA_API_URL}/vaccines', size=size)

MICROCLAUDIA_DEPLOYMENTS_SECTOR_STATS: Callable[[int], str] = \
    lambda size=5: \
    add_query_params(f'{MICROCLAUDIA_API_URL}/stats/deployments/count', groupBy='sector', size=size)
