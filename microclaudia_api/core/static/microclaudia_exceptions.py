#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class MicroClaudiaAgencyError(Exception):
    pass


class MicroClaudiaSectorError(Exception):
    pass


class MicroClaudiaAgentError(Exception):
    pass


class MicroClaudiaInstanceError(Exception):
    pass


class MicroClaudiaPatternError(ValueError):
    pass


class MicroClaudiaAuthError(Exception):
    pass


class MicroClaudiaUnauthorizedError(Exception):
    pass


class MicroClaudiaForbiddenError(Exception):
    pass


class MicroClaudiaAPIError(Exception):
    """Non-success HTTP response from an authorized API endpoint."""

    def __init__(self, url: str, status_code: int, body: str = ''):
        self.url = url
        self.status_code = status_code
        self.body = body
        detail = f': {body[:200]}' if body else ''
        super().__init__(f'HTTP {status_code} from {url!r}{detail}')


class MicroClaudiaRateLimitError(MicroClaudiaAPIError):
    """HTTP 429 from an authorized API endpoint."""


class MicroClaudiaTimeoutError(Exception):
    """HTTP request timed out before a response was received."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f'Request timed out for {url!r}')


class MicroClaudiaSchemaError(Exception):
    """JSON payload did not match the expected schema."""

    def __init__(self, func_name: str, error: Exception):
        self.func_name = func_name
        self.validation_error = error
        super().__init__(f'Invalid JSON schema in {func_name}: {error}')
