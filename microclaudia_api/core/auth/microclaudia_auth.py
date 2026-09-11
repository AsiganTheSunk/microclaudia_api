#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: FuncTools Module Import
from functools import wraps
# Note: HTTPS Module Import
from http import HTTPStatus
# Note: Typing Module Import
from typing import Any, Callable, Optional
# Note: Requests Module Import
import requests
# Note: MicroClaudia API Module Imports
from microclaudia_api.core.static.microclaudia_exceptions import (
    MicroClaudiaAPIError,
    MicroClaudiaAuthError,
    MicroClaudiaForbiddenError,
    MicroClaudiaRateLimitError,
    MicroClaudiaTimeoutError,
    MicroClaudiaUnauthorizedError,
)
from microclaudia_api.core.static.microclaudia_uri_constants import (
    MICROCLAUDIA_AUTH_REFRESH,
    MICROCLAUDIA_REQUEST_TIMEOUT,
)


def retry_on_unauthorized(func):
    """Re-run the wrapped method once after refresh-first re-authentication on 401."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except MicroClaudiaUnauthorizedError:
            self._reauthenticate()
            try:
                return func(self, *args, **kwargs)
            except MicroClaudiaUnauthorizedError as err:
                raise MicroClaudiaAuthError(
                    'Request still unauthorized after re-authentication'
                ) from err
    return wrapper


class MicroClaudiaAuth:
    def _auth_headers(self) -> dict:
        """

        """
        return {'authorization': self.authorization_token}

    @staticmethod
    def _check_authorized_response(response: Any, url: str) -> Any:
        """

        """
        if response is None:
            raise MicroClaudiaAuthError(f'No response from API for {url!r}')
        status_code = response.status_code
        if status_code == HTTPStatus.UNAUTHORIZED:
            raise MicroClaudiaUnauthorizedError(url)
        if status_code == HTTPStatus.FORBIDDEN:
            raise MicroClaudiaForbiddenError(url)
        if HTTPStatus.OK <= status_code < HTTPStatus.MULTIPLE_CHOICES:
            return response
        body = getattr(response, 'text', '') or ''
        if status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise MicroClaudiaRateLimitError(url, status_code, body)
        raise MicroClaudiaAPIError(url, status_code, body)

    def _perform_request(self, url: str, request_fn: Callable[..., Any], **kwargs) -> Any:
        """

        """
        headers = {**self._auth_headers(), **kwargs.pop('headers', {})}
        kwargs.setdefault('timeout', MICROCLAUDIA_REQUEST_TIMEOUT)
        try:
            return request_fn(url, headers=headers, **kwargs)
        except requests.Timeout as error:
            raise MicroClaudiaTimeoutError(url) from error

    def _authorized_get(self, url: str, **kwargs):
        return self._check_authorized_response(self._perform_request(url, requests.get, **kwargs), url)

    def _authorized_post(self, url: str, **kwargs):
        return self._check_authorized_response(self._perform_request(url, requests.post, **kwargs), url)

    def _authorized_patch(self, url: str, **kwargs):
        return self._check_authorized_response(self._perform_request(url, requests.patch, **kwargs), url)

    def _apply_refresh_response(self, response: Any) -> None:
        if 'Authorization' in response.headers:
            self.authorization_token = response.headers['Authorization']
        if 'refresh-token' in response.headers:
            self.refresh_token = response.headers['refresh-token']

    def _post_refresh(self) -> Any:
        try:
            return requests.post(
                MICROCLAUDIA_AUTH_REFRESH,
                json={'refreshToken': self.refresh_token},
                headers=self._auth_headers(),
                timeout=MICROCLAUDIA_REQUEST_TIMEOUT,
            )
        except requests.Timeout as error:
            raise MicroClaudiaTimeoutError(MICROCLAUDIA_AUTH_REFRESH) from error

    @staticmethod
    def _refresh_failed(response: Any) -> bool:
        return response is None or response.status_code != HTTPStatus.OK

    def _refresh_session(self, *, retry_refresh_after_login: bool = False, raise_on_failure: bool = False) -> Optional[Any]:
        """
        Refresh tokens; fall back to login. Optional second refresh for public auth_refresh().
        :param retry_refresh_after_login:
        :param raise_on_failure:
        """
        if not self.refresh_token:
            self.login(username=self.username, password=self.password)

        response = self._post_refresh()
        if self._refresh_failed(response):
            self.login(username=self.username, password=self.password)
            if retry_refresh_after_login:
                response = self._post_refresh()

        if self._refresh_failed(response):
            if raise_on_failure:
                raise MicroClaudiaAuthError('Token refresh failed')
            return None

        self._apply_refresh_response(response)
        return response

    def _reauthenticate(self, *, force_login: bool = False) -> None:
        """
        Refresh access token; fall back to full login when refresh is unavailable or fails.
        :param force_login:
        """
        if force_login:
            self.login(username=self.username, password=self.password)
            return
        self._refresh_session(retry_refresh_after_login=False, raise_on_failure=False)

