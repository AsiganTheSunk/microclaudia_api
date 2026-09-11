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
    """
    This function, will re-run the wrapped method once after refresh-first re-authentication on HTTP 401.
    :param func: Instance method to wrap.
    :return: Wrapped callable that retries once after _reauthenticate().
    """
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
        This function, will build the Authorization header used by authenticated requests.
        :return: Dict with the current Bearer authorization token.
        """
        return {'authorization': self.authorization_token}

    @staticmethod
    def _check_authorized_response(response: Any, url: str) -> Any:
        """
        This function, will map an HTTP response to success or a typed MicroClaudia exception.
        :param response: requests-like response object, or None when the call produced no response.
        :param url: Request URL included in raised errors.
        :return: The response when the status code is in the 2xx range.
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
        This function, will execute an authenticated HTTP call with the default request timeout.
        :param url: Target endpoint URL.
        :param request_fn: requests verb callable (get, post, patch, ...).
        :param kwargs: Extra arguments forwarded to request_fn (headers are merged with auth).
        :return: Raw HTTP response from request_fn.
        """
        headers = {**self._auth_headers(), **kwargs.pop('headers', {})}
        kwargs.setdefault('timeout', MICROCLAUDIA_REQUEST_TIMEOUT)
        try:
            return request_fn(url, headers=headers, **kwargs)
        except requests.Timeout as error:
            raise MicroClaudiaTimeoutError(url) from error

    def _authorized_get(self, url: str, **kwargs):
        """
        This function, will perform an authenticated GET and validate the response status.
        :param url: Target endpoint URL.
        :return: Successful HTTP response.
        """
        return self._check_authorized_response(self._perform_request(url, requests.get, **kwargs), url)

    def _authorized_post(self, url: str, **kwargs):
        """
        This function, will perform an authenticated POST and validate the response status.
        :param url: Target endpoint URL.
        :return: Successful HTTP response.
        """
        return self._check_authorized_response(self._perform_request(url, requests.post, **kwargs), url)

    def _authorized_patch(self, url: str, **kwargs):
        """
        This function, will perform an authenticated PATCH and validate the response status.
        :param url: Target endpoint URL.
        :return: Successful HTTP response.
        """
        return self._check_authorized_response(self._perform_request(url, requests.patch, **kwargs), url)

    def _apply_refresh_response(self, response: Any) -> None:
        """
        This function, will copy Authorization and refresh-token headers from a refresh response onto the client.
        :param response: Successful refresh HTTP response.
        """
        if 'Authorization' in response.headers:
            self.authorization_token = response.headers['Authorization']
        if 'refresh-token' in response.headers:
            self.refresh_token = response.headers['refresh-token']

    def _post_refresh(self) -> Any:
        """
        This function, will call the MicroClaudia auth refresh endpoint with the current refresh token.
        :api: POST /api/auth/refresh
        :return: Raw HTTP response from the refresh endpoint.
        """
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
        """
        This function, will report whether a refresh response is missing or not HTTP 200.
        :param response: Refresh HTTP response, or None.
        :return: True when refresh did not succeed.
        """
        return response is None or response.status_code != HTTPStatus.OK

    def _refresh_session(self, *, retry_refresh_after_login: bool = False, raise_on_failure: bool = False) -> Optional[Any]:
        """
        This function, will refresh session tokens, falling back to login when refresh is unavailable or fails.
        :param retry_refresh_after_login: When True, attempt one more refresh after a successful login fallback.
        :param raise_on_failure: When True, raise MicroClaudiaAuthError instead of returning None.
        :return: Successful refresh response, or None when refresh failed and raise_on_failure is False.
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
        This function, will restore a usable session via token refresh, or full login when forced.
        :param force_login: When True, skip refresh and log in with stored username and password.
        """
        if force_login:
            self.login(username=self.username, password=self.password)
            return
        self._refresh_session(retry_refresh_after_login=False, raise_on_failure=False)
