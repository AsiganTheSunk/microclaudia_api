# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: Math Module Import
from math import ceil
# Note: CSV Module Import
# Note: HTTPStatus Module Imports
from http import HTTPStatus
# Note: Typing Module Imports
from typing import (
    Tuple,
    List,
)
# Note: Requests Module Imports
from requests import (
    Response,
    Timeout,
    post,
    get
)
# Note: Tools Module Imports
from microclaudia_api.core.tools.network_ping import ping
from microclaudia_api.core.tools.countdown import (
    countdown,
    is_tty,
    tty_write,
    HIDE_CURSOR,
    SHOW_CURSOR,
    CLEAR_LINE,
    CURSOR_UP
)
from microclaudia_api.core.tools.network_call_rate_limiter import (
    call_rate_limit,
    apply_to_all_methods
)
# Note: Auth Module Imports
from microclaudia_api.core.auth.microclaudia_auth import (
    MicroClaudiaAuth,
    retry_on_unauthorized
)
# Note: Requirement Decorators Module Imports
from microclaudia_api.core.requirement.microclaudia_requirement_decorators import (
    require_microclaudia_agency_id,
    require_microclaudia_valid_id_pattern,
    require_instance_id,
    require_sector_id,
    require_agent_id,
)
# Note: Validate Json Schema Module Imports
from microclaudia_api.core.static.schemas.microclaudia_schema_validator import validate_json_schema
# Note: Schemas Module Imports
from microclaudia_api.core.static.microclaudia_exceptions import MicroClaudiaAuthError, MicroClaudiaTimeoutError
from microclaudia_api.core.static.schemas.microclaudia_schemas import (
    AGENT_SCHEMA,
    AGENTS_FROM_AGENCY_SCHEMA,
    AGENTS_LAST_VERSION_SCHEMA,
    AGENCIES_FROM_SECTOR_SCHEMA,
    ALERTS_FROM_AGENCY_SCHEMA,
    ALERTS_SCHEMA,
    AUTH_REFRESH_SCHEMA,
    INSTANCE_SCHEMA,
    INSTANCES_RESPONSE_SCHEMA,
    OSES_SCHEMA,
    PREPARE_CSV_TASK_SCHEMA,
    SECTOR_SCHEMA,
    SECTORS_FROM_INSTANCE_SCHEMA,
    SECTORS_RESPONSE_SCHEMA,
    STATS_COUNT_SCHEMA,
    STATS_NEWS_SCHEMA,
    TAGS_FROM_AGENCY_SCHEMA,
    TOTAL_STATS_FORM_EVOLUTION_SCHEMA,
    TOTAL_STATS_SCHEMA,
    USER_ROLES_SCHEMA,
    USERS_SCHEMA,
    VACCINES_FROM_AGENCY_SCHEMA,
    VACCINES_SCHEMA,
    VERSION_SCHEMA,
)
# Note: Json Module Imports
from json import (
    loads
)
# Note: URI Constants Module Imports
from microclaudia_api.core.static.microclaudia_uri_constants import (
    MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA,
    MICROCLAUDIA_STATS_EVOLUTION,
    MICROCLAUDIA_AGENCY_STATS_CONTENT,
    MICROCLAUDIA_ALERTS,
    MICROCLAUDIA_LOGIN,
    MICROCLAUDIA_INSTANCE_LIST,
    MICROCLAUDIA_AGENCY_ALERTS_CONTENT,
    MICROCLAUDIA_INSTANCE_SECTOR_CONTENT,
    MICROCLAUDIA_SECTOR_AGENCIES_CONTENT,
    MICROCLAUDIA_BASE_DOMAIN,
    MICROCLAUDIA_AGENCY_TAGS_CONTENT,
    MICROCLAUDIA_AGENCY_VACCINE_CONTENT,
    MICROCLAUDIA_TOTAL_STATS,
    MICROCLAUDIA_URL,
    MICROCLAUDIA_AGENCY_AGENT_CONTENT,
    MICROCLAUDIA_ALERTS_CSV,
    MICROCLAUDIA_TASKS,
    MICROCLAUDIA_TASK,
    MICROCLAUDIA_AGENCIES_FROM_INSTANCE,
    MICROCLAUDIA_VERSION,
    MICROCLAUDIA_OSES,
    MICROCLAUDIA_USERS,
    MICROCLAUDIA_USER_ROLES,
    MICROCLAUDIA_STATS_NEWS,
    MICROCLAUDIA_AGENTS_LAST_VERSION,
    MICROCLAUDIA_SECTOR_LIST,
    MICROCLAUDIA_INSTANCE,
    MICROCLAUDIA_SECTOR,
    MICROCLAUDIA_AGENT_CONTENT,
    MICROCLAUDIA_VACCINES,
    MICROCLAUDIA_DEPLOYMENTS_SECTOR_STATS,
    MICROCLAUDIA_REQUEST_TIMEOUT,
    MICROCLAUDIA_PING_TIMEOUT,
)
# Note: API Tools Module Imports
from microclaudia_api.core.microclaudia_api_tools import (
    add_query_params,
    sort_agents,
    filter_agents,
    order_agents
)
# Note: Time Module Imports
from time import sleep
# Note: Path Module Imports
from pathlib import Path


# Configure environ variable for a proxy
# os.environ['HTTP_PROXY'] = '<proxy>:<port>'
# os.environ['HTTPS_PROXY'] = '<proxy>:<port>'

# TODO: call_rate_limit applies to login, auth_refresh, and @retry_on_unauthorized retries,
#  which can slow 401 recovery (retry + login fallback share the same 12/min budget as data calls).
#  Consider exempting auth paths or using a separate rate-limit budget.
@apply_to_all_methods(call_rate_limit(limit_per_minute=12))
class MicroClaudiaAPI(MicroClaudiaAuth):
    def __init__(self, username: str, password: str):
        """
        This function, will instantiate the API client and log in with the provided credentials.
        :api: POST /api/login (via login)
        :param username: MicroClaudia account username used for authentication.
        :param password: MicroClaudia account password used for authentication.
        :return: None. Stores authorization_token, username, and password on the instance.
        """
        self.authorization_token = None
        self.refresh_token = None
        self.username = username
        self.password = password
        self.authorization_token, self.refresh_token = self.login(username=username, password=password)

    def health_status(self) -> bool:
        """
        This function, will verify that the MicroClaudia host is reachable and the API responds with HTTP 200.
        :api: GET / (base URL) after ICMP ping to {host}.
        :return: True if ping and the health URL succeed, False on failure or exception.
        """
        try:
            if not ping(endpoint_address=MICROCLAUDIA_BASE_DOMAIN, timeout=MICROCLAUDIA_PING_TIMEOUT).status:
                return False
            _network_response: Response = get(MICROCLAUDIA_URL, timeout=MICROCLAUDIA_REQUEST_TIMEOUT)
            return _network_response.status_code == HTTPStatus.OK
        except Exception as error:
            # TODO: It might be removed in the future
            print(f'[!]( Error ): MicroClaudia API Health Status {error}')
            return False

    def login(self, username: str, password: str) -> Tuple[str, str]:
        """
        This function, will authenticate against the MicroClaudia login endpoint and return session tokens.
        :api: POST /api/login
        :param username: Account username sent in the login request body.
        :param password: Account password sent in the login request body.
        :return: Tuple of (authorization header value, refresh-token header value).
        """
        try:
            _network_response = post(
                MICROCLAUDIA_LOGIN,
                json={"username": username, "password": password},
                timeout=MICROCLAUDIA_REQUEST_TIMEOUT,
            )
        except Timeout as error:
            raise MicroClaudiaTimeoutError(MICROCLAUDIA_LOGIN) from error
        if _network_response is None:
            raise MicroClaudiaAuthError(
                f'Login request failed (no response) for user {username!r} at {MICROCLAUDIA_LOGIN}'
            )
        if _network_response.status_code != HTTPStatus.OK:
            raise MicroClaudiaAuthError(
                f'Login failed with HTTP {_network_response.status_code} for user {username!r}'
            )
        try:
            self.authorization_token = _network_response.headers['Authorization']
            self.refresh_token = _network_response.headers['refresh-token']
        except KeyError as error:
            raise MicroClaudiaAuthError(f'Login response missing expected header: {error}') from error
        return self.authorization_token, self.refresh_token

    def auth_refresh(self) -> dict:
        """
        This function, will refresh the authentication session using the refresh token from login.
        :api: POST /api/auth/refresh body {"refreshToken": "<refresh-token from login>"}
        :return: Parsed JSON refresh response; updates authorization_token and refresh_token when returned in headers.
        """
        _network_response = self._refresh_session(retry_refresh_after_login=True, raise_on_failure=True)
        if _network_response.content:
            return validate_json_schema(loads(_network_response.content), AUTH_REFRESH_SCHEMA, self.auth_refresh)
        return {}

    @retry_on_unauthorized
    def get_instances(self, size: int | None = None, filter_by: str | None = None) -> dict:
        """
        This function, will retrieve MicroClaudia instances visible to the authenticated user.
        :api: GET /api/instances[?size={size}][&defaultFilter={filter_by}]
        :param size: Optional page size. Omitted when None (API default).
        :param filter_by: Optional API defaultFilter value (e.g. type:2).
        :return: Parsed and schema-validated JSON list or object of instances.
        """
        _microclaudia_request: str = add_query_params(
            MICROCLAUDIA_INSTANCE_LIST, size=size, defaultFilter=filter_by
        )
        _network_response: Response = self._authorized_get(_microclaudia_request)
        return validate_json_schema(loads(_network_response.content), INSTANCES_RESPONSE_SCHEMA, self.get_instances)

    @retry_on_unauthorized
    @require_instance_id
    @require_microclaudia_valid_id_pattern
    def get_instance(self, instance_id: str) -> dict:
        """
        This function, will retrieve a single MicroClaudia instance by identifier.
        :api: GET /api/instances/{instance_id}
        :param instance_id: MicroClaudia instance identifier (hex hash).
        :return: Parsed and schema-validated JSON instance object.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_INSTANCE(instance_id))
        return validate_json_schema(loads(_network_response.content), INSTANCE_SCHEMA, self.get_instance)

    @retry_on_unauthorized
    @require_instance_id
    @require_microclaudia_valid_id_pattern
    def get_sectors_from_instance(self, instance_id: str, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None, filter_by: str | None = None) -> dict:
        """
        This function, will fetch a paginated list of sectors belonging to a MicroClaudia instance.
        :api: GET /api/instances/{instance_id}/sectors?size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param instance_id: MicroClaudia instance identifier (hex hash).
        :param size: Number of sectors per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort by (e.g. name).
        :param order_by: Sort direction, asc or desc.
        :param filter_by: Tag filter applied to the request URL.
        :return: Parsed and schema-validated JSON paginated sectors response.
        """
        _microclaudia_request: str = sort_agents(MICROCLAUDIA_INSTANCE_SECTOR_CONTENT(instance_id, size, page), sort_by)
        _microclaudia_request = order_agents(_microclaudia_request, order_by)
        _microclaudia_request = filter_agents(_microclaudia_request, filter_by)
        _network_response: Response = self._authorized_get(_microclaudia_request)
        return validate_json_schema(loads(_network_response.content), SECTORS_FROM_INSTANCE_SCHEMA, self.get_sectors_from_instance)

    @retry_on_unauthorized
    def get_sectors(self) -> dict:
        """
        This function, will retrieve all sectors across the platform for the authenticated user.
        :api: GET /api/sectors
        :return: Parsed and schema-validated JSON list or object of sectors.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_SECTOR_LIST)
        return validate_json_schema(loads(_network_response.content), SECTORS_RESPONSE_SCHEMA, self.get_sectors)

    @retry_on_unauthorized
    @require_sector_id
    def get_sector(self, sector_id: str) -> dict:
        """
        This function, will retrieve a single sector by identifier.
        :api: GET /api/sectors/{sector_id}
        :param sector_id: MicroClaudia sector UUID.
        :return: Parsed and schema-validated JSON sector object.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_SECTOR(sector_id))
        return validate_json_schema(loads(_network_response.content), SECTOR_SCHEMA, self.get_sector)

    @retry_on_unauthorized
    @require_instance_id
    @require_microclaudia_valid_id_pattern
    def get_agencies_from_instance(self, instance_id: str, size: int = 200) -> dict:
        """
        This function, will list all agencies belonging to a MicroClaudia instance.
        :api: GET /api/instances/{instance_id}/agencies/all?size={size}
        :param instance_id: MicroClaudia instance identifier (hex hash).
        :param size: Maximum number of agencies to return.
        :return: Parsed and schema-validated JSON list or object of agencies for the instance.
        """
        agencies_response: Response = self._authorized_get(MICROCLAUDIA_AGENCIES_FROM_INSTANCE(instance_id, size))
        return validate_json_schema(loads(agencies_response.content), AGENCIES_FROM_SECTOR_SCHEMA, self.get_agencies_from_instance)

    @retry_on_unauthorized
    @require_sector_id
    @require_microclaudia_valid_id_pattern
    def get_agencies_from_sector(self, sector_id: str, size: int = 100, page: int = 0) -> dict:
        """
        This function, will fetch agencies that belong to the given sector.
        :api: GET /api/sectors/{sector_id}/agencies?size={size}&page={page}
        :param sector_id: MicroClaudia sector UUID.
        :param size: Number of agencies per page.
        :param page: Zero-based page index.
        :return: Parsed and schema-validated JSON paginated agencies response.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_SECTOR_AGENCIES_CONTENT(sector_id, size, page))
        return validate_json_schema(loads(_network_response.content), AGENCIES_FROM_SECTOR_SCHEMA, self.get_agencies_from_sector)

    @retry_on_unauthorized
    @require_agent_id
    @require_microclaudia_valid_id_pattern
    def get_agent(self, agent_id: str) -> object:
        """
        This function, will retrieve a single agent by identifier.
        :api: GET /api/agents/{agent_id}
        :param agent_id: MicroClaudia agent identifier.
        :return: Parsed and schema-validated JSON agent object.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_AGENT_CONTENT(agent_id))
        return validate_json_schema(loads(_network_response.content), AGENT_SCHEMA, self.get_agent)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_agents_from_agency(self, agency_id: str, size: int = 50, page: int = 0, sort_by: str | None = None, order_by: str | None = None, filter_by: str | None = None) -> dict:
        """
        Fetch a paginated list of agents for an agency.
        :api: GET /api/agencies/{agency_id}/agents?size={size}&page={page}
              [&defaultFilter={default_filter}][&sortBy={field}&orderBy=asc|desc]
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Number of agents per page.
        :param page: Zero-based page index.
        :param sort_by: Agent field to sort by (e.g. version, computerName).
        :param order_by: Sort direction, asc or desc.
        :param filter_by: API defaultFilter value (e.g. osFamily:linux, osFamily:windows).
        :return: Parsed and schema-validated JSON paginated agents response.
        """
        _microclaudia_request: str = MICROCLAUDIA_AGENCY_AGENT_CONTENT(agency_id, size, page)
        _microclaudia_request = add_query_params(_microclaudia_request, defaultFilter=filter_by)
        _microclaudia_request = sort_agents(_microclaudia_request, sort_by)
        _microclaudia_request = order_agents(_microclaudia_request, order_by)
        _network_response: Response = self._authorized_get(_microclaudia_request)
        return validate_json_schema(loads(_network_response.content), AGENTS_FROM_AGENCY_SCHEMA, self.get_agents_from_agency)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_all_agents_from_agency(self, agency_id: str, size: int = 500, page: int = 0, max_pages: int | None = None, sort_by: str | None = None, order_by: str | None = None, filter_by: str | None = None, delay: int = 30) -> dict:
        """
        This function, will paginate through all agent pages for an agency up to the API cap,
        merge them into a single collection, and show a fixed two-line live view while fetching
        (line 1 = progress bar, line 2 = countdown timer; both redrawn in place on a TTY).
        :api: Repeated GET /api/agencies/{agency_id}/agents?size={size}&page={page}
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Number of agents requested per page.
        :param page: Zero-based page index for the first request.
        :param max_pages: Optional cap on pages to fetch (e.g. for smoke tests); None fetches all allowed pages.
        :param sort_by: Agent field to sort by (e.g. version, computerName).
        :param order_by: Sort direction, asc or desc.
        :param filter_by: API defaultFilter value (e.g. osFamily:linu
        :param delay: Seconds to wait between page requests (rate-limit pacing).
        :return: Dict with total, size, page 0, and merged collection of agents.
        """
        _agents_stats_page_0: dict = self.get_agents_from_agency(agency_id, size, page, filter_by, sort_by, order_by)
        _total_agents: int = _agents_stats_page_0.get('total', 0)
        _agents_stats_pages: List[dict] = list(_agents_stats_page_0.get('collection', []))

        _tty: bool = is_tty()

        def _draw_bar(_current: int, _pages: int) -> None:
            _bar = f'-> [{_current}/{_pages}] :: <{len(_agents_stats_pages)}/{_total_agents}>'
            tty_write("\r" + CLEAR_LINE + _bar if _tty else _bar + "\n", _tty)

        tty_write(HIDE_CURSOR, _tty)
        try:
            if _total_agents and _agents_stats_pages:
                _pages = max_pages if max_pages is not None else ceil(_total_agents / size)
                _draw_bar(1, _pages)

                for _page in range(1, _pages):
                    if _tty:
                        tty_write("\n", _tty)
                    countdown(delay, tty=_tty)
                    tty_write(CURSOR_UP, _tty)

                    _page_data = self.get_agents_from_agency(agency_id, size, _page, filter_by, sort_by, order_by)
                    _collection = _page_data.get('collection', [])
                    if not _collection:
                        break
                    _agents_stats_pages.extend(_collection)
                    _draw_bar(_page + 1, _pages)
            else:
                _draw_bar(0, 0)

            tty_write("\n" + CLEAR_LINE + "\r", _tty)
        finally:
            tty_write(SHOW_CURSOR, _tty)

        _all_agents_stats: dict = {
            'total': _total_agents,
            'size': size,
            'page': 0,
            'collection': _agents_stats_pages,
        }
        return validate_json_schema(_all_agents_stats, AGENTS_FROM_AGENCY_SCHEMA, self.get_all_agents_from_agency)

    @retry_on_unauthorized
    def get_agents_last_version(self) -> dict:
        """
        This function, will retrieve the latest available agent version from the platform.
        :api: GET /api/agents/lastVersion
        :return: Parsed and schema-validated JSON object with last version information.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_AGENTS_LAST_VERSION)
        return validate_json_schema(loads(_network_response.content), AGENTS_LAST_VERSION_SCHEMA, self.get_agents_last_version)

    @retry_on_unauthorized
    def get_stats(self, section: str, group_by: str, agency_id: str | None = None, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None) -> dict | list:
        """
        Fetch count statistics grouped by a field (agency-scoped or global).
        :api: GET /api/agencies/{agency_id}/stats/{section}/count?groupBy={group_by}&size={size}&page={page}
              or GET /api/stats/{section}/count?groupBy={group_by}&size={size}&page={page}
              or GET /api/stats/deployments/count?groupBy=sector&size={size}
        :param section: Stats section (e.g. agents, alerts, deployments).
        :param group_by: Grouping field (e.g. version, os, status, computer, vaccine, sector).
        :param agency_id: When set, use the agency-scoped stats endpoint; omit for global.
        :param size: Maximum number of grouped rows (or page size).
        :param page: Zero-based page index (ignored for deployments).
        :param sort_by: Optional field to sort grouped results by.
        :param order_by: Optional sort direction, asc or desc.
        :return: Parsed JSON statistics payload (schema validation left to named helpers).
        """
        if section == 'deployments':
            _microclaudia_request: str = MICROCLAUDIA_DEPLOYMENTS_SECTOR_STATS(size)
        elif agency_id is not None:
            _microclaudia_request = MICROCLAUDIA_AGENCY_STATS_CONTENT_DATA(
                agency_id, section, group_by, size, page
            )
        else:
            _microclaudia_request = MICROCLAUDIA_AGENCY_STATS_CONTENT(section, group_by, size, page)
        _microclaudia_request = sort_agents(_microclaudia_request, sort_by)
        _microclaudia_request = order_agents(_microclaudia_request, order_by)
        _network_response: Response = self._authorized_get(_microclaudia_request)
        return loads(_network_response.content)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_version_agents_stats_from_agency(self, agency_id: str, size: int = 10, page: int = 0) -> dict:
        """
        This function, will fetch agent count statistics for an agency grouped by agent version.
        :api: GET /api/agencies/{agency_id}/stats/agents/count?groupBy=version&size={size}&page={page}
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index for pagination.
        :return: Parsed and schema-validated JSON with grouped version statistics.
        """
        return validate_json_schema(
            self.get_stats('agents', 'version', agency_id=agency_id, size=size, page=page),
            STATS_COUNT_SCHEMA,
            self.get_version_agents_stats_from_agency,
        )

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_os_agents_stats_from_agency(self, agency_id: str, size: int = 10, page: int = 0) -> List[dict]:
        """
        This function, will fetch agent count statistics for an agency grouped by operating system.
        :api: GET /api/agencies/{agency_id}/stats/agents/count?groupBy=os&size={size}&page={page}
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index for pagination.
        :return: Parsed and schema-validated JSON with grouped OS statistics.
        """
        return validate_json_schema(
            self.get_stats('agents', 'os', agency_id=agency_id, size=size, page=page),
            STATS_COUNT_SCHEMA,
            self.get_os_agents_stats_from_agency,
        )

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_status_agents_stats_from_agency(self, agency_id: str, size: int = 50, page: int = 0) -> List[dict]:
        """
        This function, will fetch agent count statistics for an agency grouped by agent status.
        :api: GET /api/agencies/{agency_id}/stats/agents/count?groupBy=status&size={size}&page={page}
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index for pagination.
        :return: Parsed and schema-validated JSON with grouped status statistics.
        """
        return validate_json_schema(
            self.get_stats('agents', 'status', agency_id=agency_id, size=size, page=page),
            STATS_COUNT_SCHEMA,
            self.get_status_agents_stats_from_agency,
        )

    @retry_on_unauthorized
    def get_os_stats_from_agents(self, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None) -> dict:
        """
        This function, will fetch global agent count statistics grouped by operating system.
        :api: GET /api/stats/agents/count?groupBy=os&size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort grouped results by.
        :param order_by: Sort direction, asc or desc.
        :return: Parsed JSON global OS agent statistics.
        """
        return validate_json_schema(
            self.get_stats('agents', 'os', size=size, page=page, sort_by=sort_by, order_by=order_by),
            STATS_COUNT_SCHEMA,
            self.get_os_stats_from_agents,
        )

    @retry_on_unauthorized
    def get_versions_stats_from_agents(self, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None) -> dict:
        """
        This function, will fetch global agent count statistics grouped by agent version.
        :api: GET /api/stats/agents/count?groupBy=version&size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort grouped results by.
        :param order_by: Sort direction, asc or desc.
        :return: Parsed JSON global version agent statistics.
        """
        return validate_json_schema(
            self.get_stats('agents', 'version', size=size, page=page, sort_by=sort_by, order_by=order_by),
            STATS_COUNT_SCHEMA,
            self.get_versions_stats_from_agents,
        )

    @retry_on_unauthorized
    def get_status_stats_from_agents(self, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None) -> dict:
        """
        This function, will fetch global agent count statistics grouped by agent status.
        :api: GET /api/stats/agents/count?groupBy=status&size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort grouped results by.
        :param order_by: Sort direction, asc or desc.
        :return: Parsed JSON global status agent statistics.
        """
        return validate_json_schema(
            self.get_stats('agents', 'status', size=size, page=page, sort_by=sort_by, order_by=order_by),
            STATS_COUNT_SCHEMA,
            self.get_status_stats_from_agents,
        )

    @retry_on_unauthorized
    def get_alerts(self, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None, filter_by: str | None = None) -> dict:
        """
        This function, will fetch a paginated list of alerts across all agencies with optional status filter.
        :api: GET /api/alerts?size={size}&page={page}[&filter=status:0|status:1][&sortBy={field}&orderBy=asc|desc]
        :param size: Number of alerts per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort by.
        :param order_by: Sort direction, asc or desc.
        :param filter_by: Alert status filter (e.g. status:1 or status:0).
        :return: Parsed and schema-validated JSON paginated global alerts response.
        """
        _microclaudia_request: str = sort_agents(MICROCLAUDIA_ALERTS(size, page), sort_by)
        _microclaudia_request = order_agents(_microclaudia_request, order_by)
        _microclaudia_request = add_query_params(_microclaudia_request, filter=filter_by)

        _network_response: Response = self._authorized_get(_microclaudia_request)
        return validate_json_schema(loads(_network_response.content), ALERTS_SCHEMA, self.get_alerts)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_alerts_from_agency(self, agency_id: str, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None, filter_by: str | None = None) -> dict:
        """
        This function, will fetch a paginated list of alerts for an agency and validate the response schema.
        :api: GET /api/agencies/{agency_id}/alerts?size={size}&page={page}[&filter=status:0|status:1][&sortBy={field}&orderBy=asc|desc]
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Number of alerts per page.
        :param page: Zero-based page index.
        :param sort_by: Alert field to sort by.
        :param order_by: Sort direction, asc or desc.
        :param filter_by: Filter expression passed to the alerts endpoint.
        :return: Parsed and schema-validated JSON alerts response.
        """
        _microclaudia_request: str = sort_agents(MICROCLAUDIA_AGENCY_ALERTS_CONTENT(agency_id, size, page), sort_by)
        _microclaudia_request = order_agents(_microclaudia_request, order_by)
        _microclaudia_request = add_query_params(_microclaudia_request, filter=filter_by)
        _network_response: Response = self._authorized_get(_microclaudia_request)
        return validate_json_schema(loads(_network_response.content), ALERTS_FROM_AGENCY_SCHEMA, self.get_alerts_from_agency)

    @retry_on_unauthorized
    def export_alerts_csv(self, output_path: str = 'Alertas.csv', max_retries: int = 30, pooling_interval: int = 5) -> bool:
        """
        Replicate the UI alerts CSV export: preparecsv → poll /api/tasks → download to output_path.
        :api: GET /api/alerts/preparecsv then GET /api/tasks then GET /api/tasks/{task_id}
        :param output_path: Local path to write the downloaded CSV bytes.
        :param max_retries: Maximum number of polling attempts before giving up.
        :param pooling_interval: Seconds to wait between polling attempts.
        :return: True if the file was written; False if Alertas.csv never completes or the download is empty.
        """
        _task_name: str = 'Alertas.csv'
        _prepare: Response = self._authorized_get(MICROCLAUDIA_ALERTS_CSV)
        if _prepare.content and _prepare.content.strip():
            validate_json_schema(loads(_prepare.content), PREPARE_CSV_TASK_SCHEMA, self.export_alerts_csv)

        _task: dict | None = None
        for _attempt in range(max_retries + 1):
            sleep(pooling_interval)
            _tasks: List[dict] = loads(self._authorized_get(MICROCLAUDIA_TASKS).content) or []
            _task = next((t for t in _tasks if t.get('name') == _task_name), None)
            if _task and _task.get('complete'):
                break
            _label: str = (_task or {}).get('id', _task_name)
            print(f' | ( Task ): [ {_label} ] - (Pending) Waiting {pooling_interval}s ...')
        else:
            return False

        print(f' | ( Task ): [ {_task["id"]} ] - (Completed) Retrieving Data ...')
        _csv: Response = self._authorized_get(MICROCLAUDIA_TASK(_task['id']))
        if not _csv.content:
            return False
        Path(output_path).write_bytes(_csv.content)
        return True

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_computer_stats_from_alerts(self, agency_id: str, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None) -> dict:
        """
        This function, will fetch alert count statistics grouped by computer for a given agency_id.
        :api: GET /api/agencies/{agency_id}/stats/alerts/count?groupBy=computer&size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param agency_id: MicroClaudia agency id.
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort grouped results by.
        :param order_by: Sort direction, asc or desc.
        :return: Parsed JSON computer alert statistics.
        """
        return validate_json_schema(
            self.get_stats(
                'alerts', 'computer', agency_id=agency_id, size=size, page=page,
                sort_by=sort_by, order_by=order_by,
            ),
            STATS_COUNT_SCHEMA,
            self.get_computer_stats_from_alerts,
        )

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_vaccine_stats_from_alerts(self, agency_id: str, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None) -> dict:
        """
        This function, will fetch alert count statistics grouped by vaccine for a given agency_id.
        :api: GET /api/agencies/{agency_id}/stats/alerts/count?groupBy=vaccine&size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param agency_id: MicroClaudia agency id.
        :param size: Maximum number of grouped rows per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort grouped results by.
        :param order_by: Sort direction, asc or desc.
        :return: Parsed JSON vaccine alert statistics.
        """
        return validate_json_schema(
            self.get_stats(
                'alerts', 'vaccine', agency_id=agency_id, size=size, page=page,
                sort_by=sort_by, order_by=order_by,
            ),
            STATS_COUNT_SCHEMA,
            self.get_vaccine_stats_from_alerts,
        )

    @retry_on_unauthorized
    def get_vaccines(self, size: int = 50) -> dict:
        """
        This function, will retrieve global vaccine records across the platform.
        :api: GET /api/vaccines?size={size}
        :param size: Maximum number of vaccine records to return.
        :return: Parsed and schema-validated JSON paginated vaccines response.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_VACCINES(size))
        return validate_json_schema(loads(_network_response.content), VACCINES_SCHEMA, self.get_vaccines)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_vaccines_from_agency(self, agency_id: str, size: int = 100, page: int = 0, sort_by: str | None = None, order_by: str | None = None, filter_by: str | None = None) -> dict:
        """
        This function, will fetch a paginated list of vaccines configured for an agency.
        :api: GET /api/agencies/{agency_id}/vaccines?size={size}&page={page}[&sortBy={field}&orderBy=asc|desc]
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Number of vaccine records per page.
        :param page: Zero-based page index.
        :param sort_by: Field to sort by.
        :param order_by: Sort direction, asc or desc.
        :param filter_by: Tag filter applied to the request URL.
        :return: Parsed and schema-validated JSON paginated vaccines response.
        """
        _microclaudia_request: str = sort_agents(MICROCLAUDIA_AGENCY_VACCINE_CONTENT(agency_id, size, page), sort_by)
        _microclaudia_request = order_agents(_microclaudia_request, order_by)
        _microclaudia_request = filter_agents(_microclaudia_request, filter_by)
        _network_response: Response = self._authorized_get(_microclaudia_request)
        return validate_json_schema(loads(_network_response.content), VACCINES_FROM_AGENCY_SCHEMA, self.get_vaccines_from_agency)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_tags_from_agency(self, agency_id: str, size: int = 10, page:int = 0) -> dict:
        """
        Fetch a paginated list of tags defined for an agency.
        :api: GET /api/agencies/{agency_id}/tags?size={size}&page={page}
        :param agency_id: MicroClaudia agency identifier (hex hash).
        :param size: Number of tags per page.
        :param page: Zero-based page index.
        :return: Parsed and schema-validated JSON tags response ({"tags": [...]}).
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_AGENCY_TAGS_CONTENT(agency_id, size, page))
        return validate_json_schema(loads(_network_response.content), TAGS_FROM_AGENCY_SCHEMA, self.get_tags_from_agency)

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def get_tags_from_agent(self, agent_id: str) -> List[str]:
        """
        This function, will query the tags currently assigned to the specified agent.
        :api: GET /api/agents/{agent_id}
        :param agent_id: MicroClaudia agent identifier (hex hash).
        :return: List of the agent's tag names (empty list when none are set).
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_AGENT_CONTENT(agent_id))

        # TODO: add schema validation before returning the dict
        # TODO: Check for error: b'{"timestamp":1780592650823,"status":404,"error":"feedback.api.error.","message":"agent.notfound"}'
        return validate_json_schema(loads(_network_response.content), AGENT_SCHEMA, self.get_tags_from_agent).get('tags', [])

    @retry_on_unauthorized
    def get_tags_from_agents(self, agent_ids: List[str]) -> dict:
        """
        This function, will query the tags currently assigned to each of the specified agents.
        :api: For each agent, GET /api/agents/{agent_id}
        :param agent_ids: List of MicroClaudia agent identifiers to query.
        :return: Dict mapping each agent identifier to its list of tag names.
        """
        _results: dict = {}
        for _agent_id in agent_ids:
            _results[f'{_agent_id}'] = self.get_tags_from_agent(agent_id=_agent_id)
        return _results

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def add_tags_to_agent(self, agent_id: str, tags: List[str]) -> List[str]:
        """
        This function, will append tags to the specified agent without removing its existing tags.
        :api: GET /api/agents/{agent_id} to read current tags, then PATCH /api/agents/{agent_id}
        body {"tags": [...]} with the merged tag list.
        :param agent_id: MicroClaudia agent identifier (hex hash).
        :param tags: Tag names to add to the agent.
        :return: List of the agent's tags after the merge.
        """
        return self.set_tags_to_agent(agent_id=agent_id, tags=self.get_tags_from_agent(agent_id=agent_id) + tags)

    @retry_on_unauthorized
    def add_tags_to_agents(self, agent_ids: List[str], tags: List[str]) -> dict:
        """
        This function, will append tags to each of the specified agents without removing their existing tags.
        :api: For each agent, GET /api/agents/{agent_id} then PATCH /api/agents/{agent_id}
        body {"tags": [...]} with the merged tag list.
        :param agent_ids: List of MicroClaudia agent identifiers to update.
        :param tags: Tag names to add to each agent.
        :return: Dict mapping each agent identifier to its list of tags after the merge.
        """
        _results: dict = {}
        for _agent_id in agent_ids:
            _results[f'{_agent_id}'] = self.add_tags_to_agent(agent_id=_agent_id, tags=tags)
        return _results

    @retry_on_unauthorized
    @require_microclaudia_agency_id
    @require_microclaudia_valid_id_pattern
    def set_tags_to_agent(self, agent_id: str, tags: List[str]) -> List[str]:
        """
        This function, will replace the full tag set on the specified agent with the given list.
        :api: PATCH /api/agents/{agent_id} body {"tags": ["{tag}", ...]}
        :param agent_id: MicroClaudia agent identifier (hex hash).
        :param tags: List of tag names to apply, replacing any existing tags.
        :return: List of the agent's tags after the update.
        """
        _network_response: Response = self._authorized_patch(MICROCLAUDIA_AGENT_CONTENT(agent_id), json={'tags': tags})
        # TODO: Check for error: b'{"timestamp":1780592650823,"status":404,"error":"feedback.api.error.","message":"agent.notfound"}'
        return validate_json_schema(loads(_network_response.content), AGENT_SCHEMA, self.set_tags_to_agent).get('tags', [])

    @retry_on_unauthorized
    def set_tags_to_agents(self, agent_ids: List[str], tags: List[str]) -> dict:
        """
        This function, will replace the full tag set on each agent with the given list.
        :api: PATCH /api/agents/{agent_id} body {"tags": ["{tag}", ...]}
        :param agent_ids: List of agent identifiers to update.
        :param tags: List of tag names to apply.
        :return: List of parsed JSON or status objects per agent.
        """
        _results: dict = {}
        for _agent_id in agent_ids:
            _results[f'{_agent_id}'] = self.set_tags_to_agent(agent_id=_agent_id, tags=tags)
        return _results

    @retry_on_unauthorized
    @require_microclaudia_valid_id_pattern
    def remove_tags_from_agent(self, agent_id: str, tags: List[str]) -> List[str]:
        """
        This function, will remove the given tags from the specified agent, keeping any other existing tags.
        :api: GET /api/agents/{agent_id} to read current tags, then PATCH /api/agents/{agent_id}
        body {"tags": [...]} with the remaining tags.
        :param agent_id: MicroClaudia agent identifier (hex hash).
        :param tags: Tag names to remove; tags not present on the agent are ignored.
        :return: List of the agent's remaining tags after removal.
        """
        _agent_tags: List[str] = self.get_tags_from_agent(agent_id)
        return self.set_tags_to_agent(agent_id, tags=[_tag for _tag in _agent_tags if _tag not in tags])

    @retry_on_unauthorized
    def remove_tags_from_agents(self, agent_ids: List[str], tags: List[str]) -> dict:
        """
        This function, will remove the given tags from each of the specified agents, keeping their other tags.
        :api: For each agent, GET /api/agents/{agent_id} then PATCH /api/agents/{agent_id}
        body {"tags": [...]} with the remaining tags.
        :param agent_ids: List of MicroClaudia agent identifiers to update.
        :param tags: Tag names to remove; tags not present on an agent are ignored.
        :return: Dict mapping each agent identifier to its list of remaining tags.
        """
        _results: dict = {}
        for _agent_id in agent_ids:
            _results[f'{_agent_id}'] = self.remove_tags_from_agent(_agent_id, tags=tags)
        return _results

    @retry_on_unauthorized
    @require_microclaudia_valid_id_pattern
    def clear_tags_from_agent(self, agent_id: str) -> List[str]:
        """
        This function, will remove all tags from the specified agent.
        :api: PATCH /api/agents/{agent_id} body {"tags": []}
        :param agent_id: MicroClaudia agent identifier (hex hash).
        :return: List of the agent's tags after clearing (an empty list).
        """
        return self.set_tags_to_agent(agent_id, tags=[])

    @retry_on_unauthorized
    def clear_tags_from_agents(self, agent_ids: List[str]) -> dict:
        """
        This function, will remove all tags from each of the specified agents.
        :api: For each agent, PATCH /api/agents/{agent_id} body {"tags": []}
        :param agent_ids: List of MicroClaudia agent identifiers to update.
        :return: Dict mapping each agent identifier to its list of tags after clearing (empty lists).
        """
        _results: dict = {}
        for _agent_id in agent_ids:
            _results[f'{_agent_id}'] = self.clear_tags_from_agent(_agent_id)
        return _results

    @retry_on_unauthorized
    def get_deployments_sector_stats(self, size: int = 5) -> dict:
        """
        This function, will retrieve deployment counts grouped by sector.
        :api: GET /api/stats/deployments/count?groupBy=sector&size={size}
        :param size: Maximum number of sector groups to return.
        :return: Parsed and schema-validated JSON stats array.
        """
        return validate_json_schema(
            self.get_stats('deployments', 'sector', size=size),
            STATS_COUNT_SCHEMA,
            self.get_deployments_sector_stats,
        )

    @retry_on_unauthorized
    def get_total_stats(self) -> dict:
        """
        This function, will fetch platform-wide aggregate statistics totals.
        :api: GET /api/stats/totals
        :return: Parsed and schema-validated JSON totals statistics object.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_TOTAL_STATS)
        return validate_json_schema(loads(_network_response.content), TOTAL_STATS_SCHEMA, self.get_total_stats)

    @retry_on_unauthorized
    def get_total_stats_evolution(self, evolution_id: int = 7) -> dict:
        """
        This function, will fetch historical evolution statistics for a given evolution metric id.
        :api: GET /api/stats/evolution/{evolution_id}
        :param evolution_id: Evolution series identifier (default 7).
        :return: Parsed and schema-validated JSON evolution time-series data.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_STATS_EVOLUTION(evolution_id))
        return validate_json_schema(loads(_network_response.content), TOTAL_STATS_FORM_EVOLUTION_SCHEMA, self.get_total_stats_evolution)

    @retry_on_unauthorized
    def get_stats_news(self) -> dict:
        """
        This function, will retrieve platform news statistics.
        :api: GET /api/stats/news
        :return: Parsed and schema-validated JSON list or object of news statistics.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_STATS_NEWS)
        return validate_json_schema(loads(_network_response.content), STATS_NEWS_SCHEMA, self.get_stats_news)

    @retry_on_unauthorized
    def get_version(self) -> dict:
        """
        This function, will retrieve the MicroClaudia API version.
        :api: GET /api/version
        :return: Parsed and schema-validated JSON object with version information.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_VERSION)
        return validate_json_schema(loads(_network_response.content), VERSION_SCHEMA, self.get_version)

    @retry_on_unauthorized
    def get_oses(self) -> dict:
        """
        This function, will retrieve operating system values from the platform.
        :api: GET /api/oses
        :return: Parsed and schema-validated JSON list or object of operating systems.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_OSES)
        return validate_json_schema(loads(_network_response.content), OSES_SCHEMA, self.get_oses)

    @retry_on_unauthorized
    def get_users(self, size: int = 50) -> object:
        """
        This function, will retrieve users from the platform.
        :api: GET /api/users?size={size}
        :param size: Maximum number of users to return.
        :return: Parsed and schema-validated JSON paginated users response.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_USERS(size))
        return validate_json_schema(loads(_network_response.content), USERS_SCHEMA, self.get_users)

    @retry_on_unauthorized
    def get_user_roles(self) -> dict:
        """
        This function, will retrieve user roles from the platform.
        :api: GET /api/users/roles
        :return: Parsed and schema-validated JSON list or object of user roles.
        """
        _network_response: Response = self._authorized_get(MICROCLAUDIA_USER_ROLES)
        return validate_json_schema(loads(_network_response.content), USER_ROLES_SCHEMA, self.get_user_roles)
